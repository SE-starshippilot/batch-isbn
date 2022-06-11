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

def getBestMatchEdition(correct:dict, editionList:list)->dict:
    accessEditionPage = lambda editionID: accessPage(conf.EDITION_QUERY_URL, editionID, postfix='.json?')
    maxSimilarity = calcMaxSimilarity(correct)
    bestMatchEdition = (None, -1)
    editionNum = 0
    for editionID in editionList:
        print(f'\t\t Handling edition No.{editionNum}')
        editionNum += 1
        editionPage = accessEditionPage(editionID)
        editionInfo, editionSimilarity =  calcEditionSimilarity(editionPage, correct)
        if editionSimilarity > bestMatchEdition[1]:
            bestMatchEdition = (editionInfo, editionSimilarity)
        if editionSimilarity == maxSimilarity:
            break
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
    import traceback
    def logError(index:int, err:int)->None:
        global df
        df.loc[index, 'Notes'] = conf.ERROR_CODE[err]
    global df
    fileName = '/Users/shitianhao/Documents/lib work/test.xls'
    df = importData(fileName)

    # Main Loop
    try:
         for idx in df.index:
            print(f'Handling {df.loc[idx, "Title"]}')
            if isinstance(df.loc[idx, conf.EXCEL_ATTRIBUTES[0]+conf.FOUND_ATTRIBUTE_POSTFIX], str):
                df.loc[idx, 'Notes'] = 'ISBN already available'
            elif isinstance(df.loc[idx, 'Notes'], str):
                pass
            else:
                bookInfo, editionList = getBookInfo(df.loc[idx, convert(conf.BOOK_ATTRIBUTES[0])]) # BOOK_ATTRIBUTE[0] is title
                print(f'\t Edition number:{len(editionList)}')
                if not(bookInfo):
                    df.loc[idx, 'Notes'] = 'No information found'
                    continue
                correctEditionInfo = getCorrectEditionInfo(df.loc[idx, :]) 
                bestMatchEdition = getBestMatchEdition(correctEditionInfo, editionList)
                concatInfo = {**bookInfo, **bestMatchEdition}
                for attr in conf.EXCEL_ATTRIBUTES:
                    attrValue = concatInfo.get(attr, None)
                    if attrValue is None: continue
                    if isinstance(attrValue, list): attrValue = ''.join(attrValue)
                    df.loc[idx, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
    except Exception as e:
        traceback.print_exc()
        exportData(fileName, df, overwrite=True)
    else:
        exportData(fileName, df)


    
def main():
    global df
    inFileName = getFilePath(useGUI=True)
    df = importData(inFileName)
    pass


if __name__ == '__main__':
    debug()