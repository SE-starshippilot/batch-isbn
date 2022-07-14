import config as conf

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

def getBookInfo(titleAndAuthor:list)->list:
    """
    returns a dictionary containing the book title, author and a list of all the edition ID
    """
    bookURL = conf.BOOK_QUERY_URL + parse.quote_plus(titleAndAuthor[0])
    bookPage = accessPage(bookURL)
    bookInfo = {} # founded book information
    editionInfo = [] # found edition information
    useManual = False
    if bookPage['numFound']:
        firstWork = bookPage['docs'][0] # pick the most similar result
        for idx, attr in enumerate(conf.BOOK_ATTRIBUTES[:-1]):
            info = firstWork.get(attr, '')
            bookInfo[attr] = info
            if not(info) or isWrongInfo(info, titleAndAuthor[idx]) < conf.HIGHBOUND: 
                useManual = True # If the retrived information is empty or it is too different from the correct one
        editionInfo = firstWork.get(conf.BOOK_ATTRIBUTES[-1]) # Assuming for a work, there is at least one edition
    return bookInfo, editionInfo, useManual # TODO: Why did I separate edition info in the first place?

def getBestMatchEdition(correct:dict, editionList:list)->dict:
    accessEditionPage = lambda editionID: accessPage(conf.EDITION_QUERY_URL, editionID, postfix='.json?')
    maxSimilarity = calcMaxSimilarity(correct)
    bestMatchEdition = (None, -1)
    editionNum = 0
    for editionID in editionList:
        print(f'\t\t Handling edition No.{editionNum}') # Need to change for logging
        editionNum += 1
        editionPage = accessEditionPage(editionID)
        editionInfo, editionSimilarity =  calcEditionSimilarity(editionPage, correct)
        if editionSimilarity > bestMatchEdition[1]:
            bestMatchEdition = (editionInfo, editionSimilarity)
        if editionSimilarity == maxSimilarity:
            break
    return bestMatchEdition[0]

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