import config as conf

import json
import time
import requests
import logging
import pandas as pd
from urllib import parse

from utils import *
import config

def accessPage(pageURL)->json:
    """
    access a page from a root node specified by id and postfix
    returns a json object if found
    """
    trials = 0
    while True:
        conf.window['-Log-'].update(value=f'Accessing {pageURL}', append=True)
        reason = ''
        try:
            page = requests.get(pageURL)
            reason = page.reason
            assert page.ok
        except Exception:
            conf.window['-Log-'].update(value=f'Error when accessing {pageURL}: {reason}', append=True)
            if trials < conf.MAXIMUM_TRIALS:
                trials += 1
                conf.window['-Log-'].update(value=f'Retrying for {trials} time.', append=True)
                time.sleep(1)
            else:
                conf.window['-Log-'].update(value=f'Maximum trials exceeded. Aborting...', append=True)
                return ''
        else:
            return json.loads(page.text)

def getBookInfo(currentRow:pd.Series)->list:
    """
    returns a dictionary containing the book title, author and a list of all the edition ID
    """
    def getBestMatchEdition(editionList:list)->dict:
        nonlocal currentRow
        accessEditionPage = lambda editionID: accessPage(conf.EDITION_QUERY_URL + editionID + '.json?', append=True)
        bestMatchEdition = (None, -1)
        for editionID in editionList:
            conf.window['-Log-'].update(value=f'Handling {editionID}', append=True) # Need to change for logging
            editionPage = accessEditionPage(editionID)
            editionInfo, editionSimilarity =  calcEditionSimilarity(editionPage, currentRow)
            if editionSimilarity > bestMatchEdition[1]:
                bestMatchEdition = (editionInfo, editionSimilarity)
            if bestMatchEdition[1] > 110: # If publisher & edition is the same, quit searching.
                break
        conf.window['-Log-'].update(value=f'Registering {bestMatchEdition[0]} as best match edition.', append=True)
        return bestMatchEdition[0]
    bookURL = conf.BOOK_QUERY_URL + parse.quote_plus(currentRow['Title'])
    bookPage = accessPage(bookURL)
    bookInfo = {} # founded book information
    if bookPage['numFound']:
        firstWork = bookPage['docs'][0] # pick the most similar result
        for attr in conf.QUERY_FIELDS: # check if title and author matches
            retAttr = firstWork.get(attr)
            if retAttr is None or isWrongInfo(retAttr, currentRow[conf.QUERY_2_EXCEL[attr]]): 
                raise AutomateError(f"the retrived book's {attr} doesn't ma··tch")
            bookInfo[attr] = retAttr
        conf.window['-Log-'].update(value=f'Matching editions:', append=True)
        editionInfo = getBestMatchEdition(firstWork.get('edition_key'))
        return {**bookInfo, **editionInfo}
    raise AutomateError('No book found')



def debug():
    # docs = getBook("The+Elements+of+Styles")
    config.dictConfig(conf.LOGGING_CONFIGURE)
    bookInfo = None

    # Return book info test
    # There could be more than one matches, and we pick the most similar one as the result
    bookInfo = getBookInfo("Hamlet")['docs'][0]
    with open('sampleBookInfo.json', 'w') as f:
        json.dump(bookInfo, f, indent=2) if bookInfo else 'Not Found'


if __name__ == '__main__':
    debug()