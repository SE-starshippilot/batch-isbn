import logging
import json
import time
import pandas as pd
import PySimpleGUI as sg

import logging.config
from query import *
from file_io import *
from utils import *
import config as conf
        

def createMainWindow():
    checkbox_list = [
            sg.Checkbox(
                text='add retrived info', key='-Add-'
            ),
            sg.Checkbox(
                text='reset progress', key='-Reset-'
            )
        ]
    progress_list = [
        [
            sg.Multiline(
                size=(40, 50), enter_submits=False, autoscroll=True, key='-Log-'
            )
        ],
        [
            sg.ProgressBar(
                size=(20, 10), max_value=100, orientation='h', bar_color=('green', 'white'), key='-Prog-'
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
            ),
            sg.Button(
                button_text='save as...', tooltip='preview the document you selected', disabled=True, enable_events=True, key='-Save-', button_color='black on grey'
            )
        ],
        checkbox_list,
        [
            sg.Button(
                button_text='Start', tooltip='begin/start the process', disabled=True, enable_events=True, key='-Toggle-'
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
    global df, logger, meta_dict, window

    if meta_dict['process'] and meta_dict['start'] < meta_dict['end']:
        curr_index = meta_dict['start'] + 1
        window['-Prog-'].update(current_count=curr_index)
        try:
            # for idx in range(meta_dict['start'], meta_dict['end']):
            #     currentRow = df.loc[idx, :]
            updateBuffer(curr_index)
            time.sleep(0.01)
        except Exception:
            updateBuffer("Some error occured, saving checkpoint and quitting")
            traceback.print_exc()
        else:
            meta_dict['start'] = curr_index
        window['-Log-'].update(value=conf.GUILogger.buffer)
    if meta_dict['start'] == meta_dict['end']:
        window['-Toggle-'].update(disabled=True)
        #         updateBuffer(f'Handling Book: {df.loc[idx, "Title"]}')
        #         if isinstance(currentRow['ISBN'], str): # the ISBN field is not empty
        #             df.loc[idx, 'Notes'] = 'ISBN already available'
        #             updateBuffer('ISBN already written. Skipping.')
        #         else:
        #             if currentRow.isna().sum() > 2: # If fields other than ISBN and Notes are empty
        #                 df.loc[idx, 'Notes'] = generateManualURL(currentRow['Title'])
        #                 updateBuffer('\tDetected Missing Fields. Generating URL for manual retrival.')
        #                 continue
        #             else:
        #                 try:
        #                     bookInfo = getBookInfo(currentRow)
        #                 except AutomateError:
        #                     df.loc[idx, 'Notes'] = generateManualURL(currentRow['Title'])
        #                     updateBuffer('No matching information found. Generating URL for manual retrival.')
        #                     continue
        #                 else:
        #                     updateBuffer(f"Found ISBN: {bookInfo['ISBN']}")
        #                     df.loc[idx, 'ISBN'] = bookInfo['ISBN']
        #         if meta_dict['-Add-']:
        #             updateBuffer(f"Writing found information into file...")
        #             for attr in conf.EXCEL_FIELDS:
        #                 attrValue = bookInfo.get(attr, '')
        #                 if isinstance(attrValue, list): attrValue = ', '.join(attrValue)
        #                 df.loc[idx, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
        #             updateBuffer(f"Done.")
        
    
    # df.to_excel(meta_dict['-File-'], index=False)


def main():
    global lh, window, meta_dict, df
    while True:
        event, value = window.read(timeout=10)
        if event == 'Goodbye' or event == sg.WINDOW_CLOSED:
            break
        if event == '-File-':
            df = importData(value['Browse'], True)
            meta_dict = readCheckpoint(value)
            meta_dict['end'] = len(df.index)
            window['-Prog-'].update(current_count=meta_dict['start'], max=meta_dict['end'])
            window['-Add-'].update(value=meta_dict['-Add-'], disabled=True)
            window['-Toggle-'].update(disabled=False)
        if event == '-Toggle-':
            window['-Reset-'].update(disabled=True)
            meta_dict['process'] = not(meta_dict['process'])
            window['-Toggle-'].update(text = 'Pause' if meta_dict['process'] else 'Start')
        process()
        window['-Log-'].update(value=conf.GUILogger.buffer)
    sg.popup(f'Saving checkpoint at {meta_dict["start"]}',title='Close')
    writeCheckpoint(meta_dict)    
    window.close()

df = None
window = createMainWindow()
meta_dict = {'process':False, 'start':0, 'end':-1}

if __name__ == '__main__':
    main()