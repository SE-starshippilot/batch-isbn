import config as conf

import json
import time
import logging
from urllib import parse
from logging import config
import requests
import numpy as np

from utils import strMatch

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

def getBookInfo(bookName:str)->list:
    """
    returns a dictionary containing the book title, author and a list of all the edition ID
    """
    accessBookPage = lambda bookName: accessPage(conf.BOOK_QUERY_URL, bookName)

    encodeName = parse.quote_plus(bookName)
    bookPage = accessBookPage(encodeName)
    bookInfo = {} # founded book information
    editionInfo = [] # found edition information
    useManual = False
    if bookPage['numFound']:
        firstWork = bookPage['docs'][0] # pick the most similar result
        for idx, attr in enumerate(conf.BOOK_ATTRIBUTES[:-1]):
            info = firstWork.get(attr, '')
            bookInfo[attr] = info
            if not(info) or strMatch(info, bookName) < conf.HIGHBOUND: 
                useManual = True
                break # If the retrived information is empty or it is too different from the correct one
        editionInfo = firstWork.get(conf.BOOK_ATTRIBUTES[-1], '') # Assuming for a work, there is at least one edition
    return bookInfo, editionInfo, useManual # TODO: Why did I separate edition info in the first place?

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