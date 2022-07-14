# import logging
from query import *
from file_io import *
from utils import *
import config as conf

df = None

def debug():
    import traceback
    global df
    fileName = '/Users/shitianhao/Documents/lib work/test.xls'
    df = importData(fileName)
    startIndex = readCheckpoint()
    endIndex = len(df.index)
    _tmpindex = startIndex

    # Main Loop
    try:
        for idx in range(startIndex, endIndex):
            currentRow = df.loc[idx, :]
            print(f'Handling {df.loc[idx, "Title"]}') # need to change to logging
            if isinstance(currentRow['ISBN'], str): # the ISBN field is not empty
                df.loc[idx, 'Notes'] = 'ISBN already available'
            else: # Retrive ISBN
                titleAndAuthor = [currentRow['Title'], currentRow['Author']]
                bookInfo, editionList, useManual = getBookInfo(titleAndAuthor)
                print(f'\t Edition number:{len(editionList)}') # need to change to logging
                if useManual:
                    df.loc[idx, 'Notes'] = generateManualURL(df.loc[idx, convert(conf.BOOK_ATTRIBUTES[0])])
                    continue
                bestMatchEdition = getBestMatchEdition(currentRow, editionList)
                concatInfo = {**bookInfo, **bestMatchEdition}
                for attr in conf.EXCEL_ATTRIBUTES:
                    attrValue = concatInfo.get(attr, '')
                    if isinstance(attrValue, list): attrValue = ''.join(attrValue)
                    df.loc[idx, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
                _tmpindex = idx
    except Exception:
        traceback.print_exc()
        writeCheckpoint(_tmpindex)
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