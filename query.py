import config as conf

import json
import time
import logging
from urllib import parse
from logging import config
import requests
import numpy as np

from utils import strMatch

def getURL(baseURL:str, value:dict)->str:
    return baseURL + parse.unquote(value)

def accessPage(pageURL)->json:
    """
    access a page from a root node specified by id and postfix
    returns a json object if found
    """
    trials = 0
    while True:
        logging.info(f'Accessing {pageURL}')
        try:
            page = requests.get(pageURL)
            reason = page.reason
            assert page.ok
        except Exception:
            logging.warning(f'Error when accessing {pageURL}')
            if trials < conf.MAXIMUM_TRIALS:
                trials += 1
                logging.warning(f'Retrying for {trials} time.')
                time.sleep(1)
            else:
                logging.error(f'Maximum trials exceeded. Aborting...')
                return ''
        else:
            return json.loads(page.text)

def getBookInfo(bookName:str)->list:
    """
    returns a dictionary containing the book title, author and a list of all the edition ID
    """
    bookURL = getURL(conf.BOOK_QUERY_URL, )
    accessBookPage = lambda bookName: accessPage(conf.BOOK_QUERY_URL, bookName)

    encodeName = parse.quote_plus(bookName)
    bookPage = accessBookPage(encodeName)
    bookInfo = {} # founded book information
    editionInfo = []
    if bookPage['numFound']:
        firstWork = bookPage['docs'][0]
    else:
        return bookInfo, editionInfo
    for idx, attr in enumerate(conf.BOOK_ATTRIBUTES):
        info = firstWork.get(attr, f'{attr} not found')
        if idx == 0 and strMatch(info, bookName) < conf.HIGHBOUND:
            return bookInfo, editionInfo #errcode? # If the found book title is too different with correct, terminate search
        if idx == len(conf.BOOK_ATTRIBUTES) - 1:
            editionInfo = info # the last attribute acuqires edition information
        else:
            bookInfo[attr] = info
    return bookInfo, editionInfo

def getManualURL(bookName:str, carrier:str)->str:
    return carrier + bookName

def debug():
    # docs = getBook("The+Elements+of+Styles")
    config.dictConfig(conf.LOGGING_CONFIGURE)
    bookInfo = None

    # Return book info test
    # There could be more than one matches, and we pick the most similar one as the result
    bookInfo = accessPage(conf.BOOK_QUERY_URL, "Hamlet")['docs'][0]
    with open('sampleBookInfo.json', 'w') as f:
        json.dump(bookInfo, f, indent=2) if bookInfo else 'Not Found'

    # Return an attribute for all the editions of abook
    # attrName = 'edition_key'
    # for edition in bookInfo['edition_key']:
    #     editionPage = accessPage(conf['EDITION_QUERY_URL'], edition, postfix='.json?')
    #     if attrName in editionPage.keys():
    #         print(f"{edition}'s {attrName} attribute is {editionPage[attrName]}")
    #     else:
    #         print(f'{edition} has no attribute {attrName} specified')

    # Return specific Edition Test
    # editionPage = accessPage(conf['EDITION_QUERY_URL'], 'OL31992890M', postfix='.json?')
    # with open('sampleEditionInfo.json', 'w') as wf:
    #     json.dump(editionPage, wf, indent=2)


if __name__ == '__main__':
    debug()