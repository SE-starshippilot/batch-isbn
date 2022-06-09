import json
import math
# import logging
import argparse
import pandas as pd
from urllib import parse
from query import *
from process import *
from file_io import *
import config as conf

# parser = argparse.ArgumentParser()
# parser.add_argument()
df = None
# logging.basicConfig(level=logging.INFO, format=)
class QueryError(Exception):
    def __init__(self, message, status) -> None:
        super().__init__(message, status)
        
def getBookInfo(bookName:str)->list:
    """
    returns a dictionary containing the book title, author and a list of all the edition ID
    """
    accessBookPage = lambda bookName: accessPage(conf.BOOK_QUERY_URL, bookName)['docs']

    bookName = parse.quote(bookName)
    bookPage = accessBookPage(bookName)
    if not(bookPage):
        return 0, {}
    else:
        bookPage = bookPage[0]
    bookInfo = {} # founded book information
    for idx, attr in enumerate(conf.BOOK_ATTRIBUTES):
        info = bookPage.get(attr, f'{attr} not found')
        if idx == len(conf.BOOK_ATTRIBUTES) - 1:
            return bookInfo, info # the last attribute acuqires edition information
        bookInfo[attr] = info

def getBestMatchEdition(correct:dict, editionList:list)->dict:
    accessEditionPage = lambda editionID: accessPage(conf.EDITION_QUERY_URL, editionID, postfix='.json?')
    bestMatchEdition = (None, -1)
    for editionID in editionList:
        editionPage = accessEditionPage(editionID)
        editionInfo, editionSimilarity =  calcEditionSimilarity(correct, editionPage)
        if editionSimilarity > bestMatchEdition[1]:
            bestMatchEdition = (editionInfo, editionSimilarity)
    return bestMatchEdition[0]

def getCorrectEditionInfo(row:pd.Series)->dict:
    editionInfo = {}
    for attr in conf.EDITION_ATTRIBUTES[:2]: # publisher and publish_date
        attrInfo = row[convert(attr)]
        if isinstance(attrInfo, str) or not(np.isnan(attrInfo)):
            editionInfo[attr] = attrInfo
    return editionInfo

convert = lambda attr: conf.EXCEL_FIELD_MAP[attr]

def debug():
    def logError(index:int, err:int)->None:
        global df
        df.loc[index, 'Notes'] = conf.ERROR_CODE[err]
    global df
    fileName = '/Users/shitianhao/Documents/lib work/LibGuides Spring 2022.xls'
    df = importData(fileName)

    # Main Loop
    for idx in df.index:
        if isinstance(df.loc[idx,'ISBN'], str):
            logError(idx, 1)
            df.loc[idx, 'Notes'] = 'ISBN already available'
            print(type(df.loc[idx, 'Author']))
        else:
            bookInfo, editionList = getBookInfo(df.loc[idx, convert(conf.BOOK_ATTRIBUTES[0])]) # BOOK_ATTRIBUTE[0] is title
            editionInfo = getCorrectEditionInfo(df.loc[idx, :]) 
            bestMatchEdition = getBestMatchEdition(editionInfo, editionList)
            concatInfo = {**bookInfo, **bestMatchEdition}
            for attr in conf.EXCEL_ATTRIBUTES:
                attrValue = concatInfo[attr]
                if isinstance(attrValue, list): attrValue = ''.join(attrValue)
                df.loc[idx, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
    
    exportData(fileName, df)


    
def main():
    global df
    inFileName = getFilePath(useGUI=True)
    df = importData(inFileName)
    pass


if __name__ == '__main__':
    debug()