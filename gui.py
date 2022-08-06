import logging
import json
import time
import pandas as pd
import PySimpleGUI as sg
from functools import wraps

import logging.config
from query import *
from file_io import *
from utils import *
import config as conf
        

def createMainWindow():
    checkbox_list = [
            sg.Checkbox(
                text='add retrived info', key='-Add-'
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
            sg.FileBrowse(file_types=[("Excel Files", ".xls .xlsx"),], key='-Path-')
        ],
        [
            sg.Button(
                button_text='preview', tooltip='preview the document you selected', disabled=True, enable_events=True, key='-Preview-', button_color='black on grey'
            ),
            sg.Button(
                button_text='reset progress', tooltip='reset the checkpoint of this file', disabled=True, enable_events=True, key='-Reset-', button_color='black on grey'
            ),
            sg.In(key='Save As', enable_events=True, visible=False),
            sg.FileSaveAs(
                button_text='save as...', tooltip='preview the document you selected', disabled=True, enable_events=True, key='-Save-', button_color='black on grey', file_types=(('Excel Files', '.xls .xlsx .csv'),), default_extension='xlsx'
            )
        ],
        checkbox_list,
        [
            sg.Button(
                button_text='Start', tooltip='begin/start the process', disabled=True, enable_events=True, key='-Toggle-', button_color='black on grey'
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
    return sg.Window(title='Batch ISBN Retriver v0.1', layout=layout, size=(800, 800), modal=False)

def modalize(window_func):
    """
    Disable the buttons on the main window so that only one function is active.
    """
    @wraps(window_func)
    def wrap_window(*args, **kwargs):
            changeButtonAvail(True, '-Preview-', '-Toggle-', '-Reset-', '-Save-', '-Path-')
            window_func(*args, **kwargs)
            changeButtonAvail(False, '-Preview-', '-Toggle-', '-Reset-', '-Save-', '-Path-')
    return wrap_window


@modalize
def preview(df:pd.DataFrame):
    df_headings = list(df.columns)
    df_vals = df.loc[1:, :].fillna('')
    df_vals = df_vals.values.tolist()
    layout = [[sg.Table(headings=df_headings, values=df_vals)]]
    preview_window = sg.Window('Preview', layout, modal=True)
    while True:
        event, values = preview_window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    preview_window.close()


@modalize
def save_as(df:pd.DataFrame):
    pass
 
def process(df:pd.DataFrame):
    import traceback
    global meta_dict, window

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

def changeButtonAvail(disable:bool, *args):
    global window
    for arg in args:
        window[arg].update(disabled=disable, button_color=conf.BUTTON_APPEARANCE[disable])

def main():
    global window, meta_dict, df
    while True:
        event, value = window.read(timeout=10)
        if event == 'Goodbye' or event == sg.WINDOW_CLOSED:
            break
        if event == '-File-':
            df = importData(value['-File-'])
            meta_dict.update(readCheckpoint(value))
            meta_dict['end'] = len(df.index)
            meta_dict['save_path'] = meta_dict['-File-']
            if meta_dict['start']:
                window['-Add-'].update(value=meta_dict['-Add-'], disabled=True)
            window['-Prog-'].update(current_count=meta_dict['start'], max=meta_dict['end'])
            changeButtonAvail(False, '-Reset-', '-Toggle-', '-Preview-', '-Save-')
            updateBuffer('Default saving to the original file.')
        if event == '-Toggle-':
            window['-Add-'].update(disabled=True)
            meta_dict['-Add-'] = value['-Add-']
            if (f'{df.columns[0]}{conf.FOUND_ATTRIBUTE_POSTFIX}' in df.columns) != meta_dict['-Add-']:
                foundAttrName = [i + conf.FOUND_ATTRIBUTE_POSTFIX for i in conf.EXCEL_FIELDS]
                if meta_dict['-Add-']:
                    df = pd.concat([df, pd.DataFrame(columns=foundAttrName)])
                else:
                    df = df.drop(foundAttrName, axis=1)
            meta_dict['process'] = not(meta_dict['process'])
            changeButtonAvail(meta_dict['process'], '-Reset-', '-Preview-', '-Save-')
            window['-Toggle-'].update(text = 'Pause' if meta_dict['process'] else 'Start')
        if event == '-Reset-':
            updateBuffer('Resetted progress', clear=True)
            meta_dict['start'] = 0
            writeCheckpoint(meta_dict)
            window['-Prog-'].update(current_count=0)
            window['-Add-'].update(disabled=False)
        if event == '-Preview-':
            preview(df)
        if event == 'Save As':
            meta_dict['save_path'] = value['-Save-']
            updateBuffer(f'Now saving to {meta_dict["save_path"]}')
        process(df)
        window['-Log-'].update(value=conf.GUILogger.buffer)
    writeCheckpoint(meta_dict)
    df.to_excel(meta_dict['save_path'], index=False)
    sg.popup(f'Saving checkpoint at {meta_dict["start"]}',title='Close')
    window.close()

df = None
window = createMainWindow()
meta_dict = {'process':False, 'start':0, 'end':-1}

if __name__ == '__main__':
    main()