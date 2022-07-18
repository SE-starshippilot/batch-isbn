import logging.config
from query import *
from file_io import *
from utils import *
import config as conf

df = None
logger = None

def debug():
    import traceback
    global df, logger

    args = configparser()

    logger = configlogger(args.verbose)

    fileName = getInputDir(args.file)
    df = importData(fileName, args.addColumns)

    startIndex = readCheckpoint()
    endIndex = len(df.index)

    # Main Loop
    try:
        for idx in range(startIndex, endIndex):
            currentRow = df.loc[idx, :]
            logger.info(f'Handling Book: {df.loc[idx, "Title"]}')
            if isinstance(currentRow['ISBN'], str): # the ISBN field is not empty
                df.loc[idx, 'Notes'] = 'ISBN already available'
                logging.info('ISBN already written. Skipping.')
                continue
            else:
                if currentRow.isna().sum() > 2: # If fields other than ISBN and Notes are empty
                    df.loc[idx, 'Notes'] = generateManualURL(currentRow['Title'])
                    logging.warning('\tDetected Missing Fields. Generating URL for manual retrival.')
                    continue
                else:
                    try:
                        bookInfo = getBookInfo(currentRow)
                    except AutomateError:
                        df.loc[idx, 'Notes'] = generateManualURL(currentRow['Title'])
                        logging.warning('No matching information found. Generating URL for manual retrival.')
                        continue
                    else:
                        logging.info(f"Found ISBN: {bookInfo['ISBN']}")
                        df.loc[idx, 'ISBN'] = bookInfo['ISBN']

            if args.verbose:
                logging.info(f"Writing found information into file...")
                for attr in conf.EXCEL_FIELDS:
                    attrValue = bookInfo.get(attr, '')
                    if isinstance(attrValue, list): attrValue = ', '.join(attrValue)
                    df.loc[idx, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
                logging.info(f"Done.")
    except Exception:
        logging.error("Some error occured, saving checkpoint and quitting")
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