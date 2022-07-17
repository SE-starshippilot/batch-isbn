import config as conf

import pandas as pd
import json
import time
import logging
from urllib import parse
from logging import config
import requests
import numpy as np

from utils import *


def accessPage(pageURL)->json:
    """
    access a page from a root node specified by id and postfix
    returns a json object if found
    """
    trials = 0
    while True:
        logging.info(f'Accessing {pageURL}')
        reason = ''
        try:
            page = requests.get(pageURL)
            reason = page.reason
            assert page.ok
        except Exception:
            logging.warning(f'Error when accessing {pageURL}: {reason}')
            if trials < conf.MAXIMUM_TRIALS:
                trials += 1
                logging.warning(f'Retrying for {trials} time.')
                time.sleep(1)
            else:
                logging.error(f'Maximum trials exceeded. Aborting...')
                return ''
        else:
            return json.loads(page.text)

def getBookInfo(currentRow:pd.Series)->list:
    """
    returns a dictionary containing the book title, author and a list of all the edition ID
    """
    def getBestMatchEdition(editionList:list)->dict:
        nonlocal currentRow
        accessEditionPage = lambda editionID: accessPage(conf.EDITION_QUERY_URL + editionID + '.json?')
        bestMatchEdition = (None, -1)
        for editionID in editionList:
            print(f'\t\t Handling {editionID}') # Need to change for logging
            editionPage = accessEditionPage(editionID)
            editionInfo, editionSimilarity =  calcEditionSimilarity(editionPage, currentRow)
            if editionSimilarity > bestMatchEdition[1]:
                bestMatchEdition = (editionInfo, editionSimilarity)
        return bestMatchEdition[0]
    bookURL = conf.BOOK_QUERY_URL + parse.quote_plus(currentRow['Title'])
    bookPage = accessPage(bookURL)
    bookInfo = {} # founded book information
    if bookPage['numFound']:
        firstWork = bookPage['docs'][0] # pick the most similar result
        for attr in conf.EXCEL_FIELDS[1:3]: # check if title and author matches
            retAttr = firstWork.get(attr)
            if retAttr is None or isWrongInfo(retAttr, currentRow[attr]) < conf.HIGHBOUND: 
                raise AutomateError
            bookInfo[attr] = retAttr
        editionInfo = getBestMatchEdition(firstWork.get('edition_key'))
        return {**bookInfo, **editionInfo}
    raise AutomateError



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