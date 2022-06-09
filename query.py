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
    returns a json object
    """
    pageURL = baseURL + id + postfix
    page = requests.get(pageURL)
    assert page.ok
    return json.loads(page.text)

def debug():
    global conf
    # docs = getBook("The+Elements+of+Styles")
    with open('config.json', 'r') as jf:
        conf = json.load(jf)
    # There could be more than one matches, and we pick the most similar one as the result
    try:
        bookInfo = accessPage(conf['BOOK_QUERY_URL'], "The+Elements+of+Styles")['docs'][0]
        with open('sampleBookInfo.json', 'w') as f:
            json.dump(bookInfo, f, indent=2)
        firstEdition = bookInfo['edition_key'][1]
        editionInfo = accessPage(conf['EDITION_QUERY_URL'], 'OL31438449M', postfix='.json?')
        with open('sampleEditionInfo.json', 'w') as f:
            json.dump(editionInfo, f, indent=2)
    except AssertionError:
        print('Ouch')


if __name__ == '__main__':
    debug()