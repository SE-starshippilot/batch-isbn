import logging
import json
import pandas as pd
import PySimpleGUI as sg

import logging.config
from query import *
from file_io import *
from utils import *
import config as conf

# class GUILogger(logging.StreamHandler):
#     buffer = ''
#     def __init__(self, level=logging.WARNING):
#         logging.StreamHandler.__init__(self)
#         self.setLevel(level)

#     def __log(self, level,message):
#         if level >= self.level:
#             buffer += f'{message}\n'
    
#     def debug(self, message):
#         self.__log(logging.DEBUG, message)
        
#     def info(self, message):
#         self.__log(logging.INFO, message)
        
#     def warning(self, message):
#         self.__log(logging.WARNING, message)
        
#     def error(self, message):
#         self.__log(logging.ERROR, message)
        


def createMainWindow():
    checkbox_list = [
            sg.Checkbox(
                text='add retrived info', key='-Add-'
            ),
            sg.Checkbox(
                text='restore checkpoint', key='-Restore-'
            )
        ]
    progress_list = [
        [
            sg.Multiline(
                size=(40, 50), enter_submits=False, autoscroll=True, key='-log-'
            )
        ],
        [
            sg.ProgressBar(
                size=(20, 10), max_value=100, orientation='h', bar_color=('green', 'white')
            )
        ]
    ]
    file_list = [
        [   
            sg.Text("Select an excel doccument"),
            sg.In(
                size=(50, 1), enable_events=True, key='-File-', 
            ),
            sg.FileBrowse()
        ],
        [
            sg.Button(
                button_text='preview', tooltip='preview the document you selected', disabled=True, enable_events=True, key='-Preview-'
            )
        ],
        checkbox_list,
        [
            sg.Button(
                button_text='start/start', tooltip='begin/start the process', disabled=True, enable_events=True, key='-Toggle-'
            )
        ]
    ]
    layout = [
        [
            sg.Column(file_list),
            sg.VSeperator(),
            sg.Column(progress_list)
        ]
    ]
    return sg.Window(title='Batch ISBN Retriver v0.1', layout=layout, size=(800, 800))

def createPreviewWindow(headings, contents):
    # header = [sg.Text(i) for i in heading]
    layout = [[sg.Table(values=contents, headings=headings)]]
    return sg.Window(title='Preview', layout=layout)

def process():
    import traceback
    global df, logger

    args = configparser()

    logger = GUILogger()

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
    global lh, window
    preview = None
    start=False
    while True:
        event, value = window.read()
        if event == 'Goodbye' or event == sg.WINDOW_CLOSED:
            break
        if event == '-File-':
            df = importData(value['Browse'], True)
            # print(value)
            actionDict = readCheckpoint(value)
        if event == '-Toggle-':
            for k, v in value:
                if k != '-log-' or 'Browse':
                    pass
            # start=not(start)
            # if start:
            #     process()
        window['-log-'].update(value=conf.GUILogger.buffer)
    window.close()

window = createMainWindow()
# lh = GUILogger(logging.INFO)

if __name__ == '__main__':
    main()