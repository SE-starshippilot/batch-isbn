import json
import requests
import numpy as np
from bs4 import BeautifulSoup

conf = None

def formatTitle(title):
    f_title = title
    return f_title

def accessPage(baseURL:str, id:str, postfix:str='')->json:
    """
    access a page from a root node specified by id and postfix
    returns a json object if found
    """
    trials = 0
    while True:
        pageURL = baseURL + id + postfix
        page = requests.get(pageURL)
        try:
            assert page.ok
        except AssertionError:
            if trials < conf['MAXIMUM_TRIALS']:
                trials += 1
                print(f'{trials} trial(s) failed. Retrying...')
            else:
                print('Maximum trials exceeded. Aborting...')
                return ''
        else:    
            return json.loads(page.text)

def debug():
    global conf
    # docs = getBook("The+Elements+of+Styles")
    with open('config.json', 'r') as jf:
        conf = json.load(jf)
    # There could be more than one matches, and we pick the most similar one as the result
    # bookInfo = accessPage(conf['BOOK_QUERY_URL'], "The+Elements+of+Styles")['docs'][0]
    # with open('sampleBookInfo.json', 'w') as f:
    #     json.dump(bookInfo, f, indent=2) if bookInfo else 'Not Found'
    # firstEdition = bookInfo['edition_key'][1]
    editionInfo = accessPage(conf['EDITION_QUERY_URL'], 'OL32926552M', postfix='.json?')
    with open('sampleEditionInfo.json', 'w') as f:
        json.dump(editionInfo, f, indent=2) if editionInfo else 'Not Found'


if __name__ == '__main__':
    debug()