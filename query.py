import config as conf

import json
import time
import requests
import pandas as pd
from urllib import parse

from utils import *
import config as conf

def accessPage(pageURL)->json:
    """
    access a page from a root node specified by id and postfix
    returns a json object if found
    """
    trials = 0
    while True:
        conf.logger.debug(f'Accessing {pageURL}')
        try:
            page = requests.get(pageURL)
            assert page.ok
            return json.loads(page.text)
        except Exception as e:
            if trials < conf.MAXIMUM_TRIALS:
                trials += 1
                conf.logger.warn(f'Cannot access. Retrying for {trials} time.')
                time.sleep(1)
            else:
                conf.logger.warn(f'Maximum trials exceeded. Aborting...')
                raise NetworkUnreachableError()

def getBookInfo(currentRow:pd.Series)->list:
    """
    returns a dictionary containing the book title, author and a list of all the edition ID
    """
    def getBestMatchEdition(editionList:list)->dict:
        nonlocal currentRow
        accessEditionPage = lambda editionID: accessPage(conf.EDITION_QUERY_URL + editionID + '.json?')
        bestMatchEdition = (None, -1)
        for editionID in editionList:
            conf.logger.debug(f'Handling {editionID}') # Need to change for logging
            editionPage = accessEditionPage(editionID)
            editionInfo, editionSimilarity =  calcEditionSimilarity(editionPage, currentRow)
            if editionSimilarity > bestMatchEdition[1]:
                bestMatchEdition = (editionInfo, editionSimilarity)
            if bestMatchEdition[1] >= 110: # If publisher & edition is the same, quit searching.
                break
        conf.logger.info('Registering {bestMatchEdition[0]} as best match edition.')
        return bestMatchEdition[0]
    if  (conf.window.metadata['append'] and currentRow.isna().sum() > 2 + len(conf.EXCEL_FIELDS)) or \
        (not(conf.window.metadata['append']) and currentRow.isna().sum() > 2):
        raise MissingInfoError('Missing information in the input row.', currentRow['Title'])
    bookURL = conf.BOOK_QUERY_URL + parse.quote_plus(currentRow['Title'])
    bookPage = accessPage(bookURL)
    bookInfo = {} # founded book information
    if bookPage['numFound']:
        firstWork = bookPage['docs'][0] # pick the most similar result
        for attr in conf.QUERY_FIELDS: # check if title and author matches
            retAttr = firstWork.get(attr)
            if retAttr is None or isWrongInfo(retAttr, currentRow[conf.QUERY_2_EXCEL[attr]]): 
                raise MissingInfoError(f"the retrived book's {attr} {retAttr} doesn't match with {currentRow[conf.QUERY_2_EXCEL[attr]]}", currentRow['Title'])
            bookInfo[attr] = retAttr
        conf.logger.debug(f'Matching editions:')
        editionInfo = getBestMatchEdition(firstWork.get('edition_key'))
        if not(editionInfo.get('ISBN')):
            raise MissingInfoError('Found book, but Open Library returns no ISBN.', currentRow['Title'])
        return {**bookInfo, **editionInfo}
    raise MissingInfoError(f'No book found for {currentRow["Title"]}', currentRow['Title'])



def debug():
    # docs = getBook("The+Elements+of+Styles")
    bookInfo = None

    # Return book info test
    # There could be more than one matches, and we pick the most similar one as the result
    bookInfo = getBookInfo("Hamlet")['docs'][0]
    with open('sampleBookInfo.json', 'w') as f:
        json.dump(bookInfo, f, indent=2) if bookInfo else 'Not Found'


if __name__ == '__main__':
    debug()