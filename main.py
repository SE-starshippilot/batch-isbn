import logging.config
from query import *
from file_io import *
from utils import *
import config as conf

df = None

def debug():
    import traceback
    global df

    args = configparser()

    logging.config.dictConfig(conf.LOGGING_CONFIGURE)
    logger = logging.getLogger(__name__)

    fileName = getInputDir(args.file)
    df = importData(fileName, args.addColumns)

    startIndex = readCheckpoint()
    endIndex = len(df.index)

    # Main Loop
    try:
        for idx in range(startIndex, endIndex):
            currentRow = df.loc[idx, :]
            logger.info(f'Handling {df.loc[idx, "Title"]}')
            if isinstance(currentRow['ISBN'], str): # the ISBN field is not empty
                df.loc[idx, 'Notes'] = 'ISBN already available'
                continue
            else:
                if currentRow.isna().sum() > 1:
                    df.loc[idx, 'Notes'] = generateManualURL(currentRow['Title'])
                else:
                    try:
                        bookInfo = getBookInfo(currentRow)
                    except AutomateError:
                        df.loc[idx, 'Notes'] = generateManualURL(currentRow['Title'])
                    else:
                        df.loc[idx, 'ISBN'] = bookInfo['ISBN']
            if args.verbose:
                for attr in conf.EXCEL_FIELDS:
                    attrValue = bookInfo.get(attr, '')
                    if isinstance(attrValue, list): attrValue = ', '.join(attrValue)
                    df.loc[idx, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
    except Exception:
        traceback.print_exc()
        writeCheckpoint(idx)
    
    outName = args.out if args.out else args.file
    df.to_excel(outName, index=False)


def main():
    global df
    inFileName = getInputDir(useGUI=True)
    df = importData(inFileName)
    pass


if __name__ == '__main__':
    debug()