import config as conf

import json
import time
import logging
from logging import config
import requests
import numpy as np

def accessPage(baseURL:str, id:str, postfix:str='')->json:
    """
    access a page from a root node specified by id and postfix
    returns a json object if found
    """
    trials = 0
    while True:
        pageURL = baseURL + id + postfix
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