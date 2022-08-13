import time
import pandas as pd
import PySimpleGUI as sg
from functools import wraps

from query import *
from file_io import *
from utils import *
import config as conf
        

def createMainWindow():
    checkbox_list = [
            sg.Checkbox(
                text='add retrived info', key='-Add-', disabled=True
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
                size=(50, 1), enable_events=True, key='-File-', readonly=True
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
                button_text='Start', tooltip='begin/halt the process', disabled=True, enable_events=True, key='-Toggle-', button_color='black on grey'
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
    return sg.Window(title='Batch ISBN Retriver v0.1', layout=layout, size=(800, 800), modal=False, metadata=conf.INITIAL_METADICT)

def modalize(window_func):
    """
    Disable the buttons on the main window so that only one function is active.
    """
    @wraps(window_func)
    def wrap_window(*args, **kwargs):
            setElementDisable(True, '-Preview-', '-Toggle-', '-Reset-', '-Save-', '-Path-')
            window_func(*args, **kwargs)
            setElementDisable(False, '-Preview-', '-Toggle-', '-Reset-', '-Save-', '-Path-')
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
def choice():
    quit_program = True
    choice_window = sg.Window('Finished processing.', [[sg.T('Do you want to process another file?')], [sg.Yes(s=10), sg.No(s=10)]], disable_close=True)
    while True:
        event, value = choice_window.read()
        if event == 'Yes' or event == sg.WIN_CLOSED:
            quit_program = False
            break
        if event == 'No':
            break
    choice_window.close()
    return quit_program

def process(df:pd.DataFrame):
    import traceback
    global window

    if window.metadata['process'] and window.metadata['incomplete']:
        curr_index = window.metadata['start'] + 1
        window['-Prog-'].update(current_count=curr_index)
        try:
            # for idx in range(window.metadata['start'], window.metadata['end']):
            #     currentRow = df.loc[idx, :]
            updateBuffer(curr_index)
            time.sleep(0.01)
        except Exception:
            updateBuffer("Some error occured, saving checkpoint and quitting")
            traceback.print_exc()
        else:
            window.metadata['start'] = curr_index
            window.metadata['incomplete'] = window.metadata['start'] < window.metadata['end']
        window['-Log-'].update(value=conf.GUILogger.buffer)
    if not(window.metadata['incomplete']) and window.metadata['process']:
        df.to_excel(window.metadata['save_path'], index=False)
        updateBuffer('Removing checkpoint')
        setElementDisable(True, '-Toggle-')
        setElementDisable(False, '-Reset-', '-Preview-', '-Save-')
        window.metadata['process'] = False
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
        #         if window.metadata['-Add-']:
        #             updateBuffer(f"Writing found information into file...")
        #             for attr in conf.EXCEL_FIELDS:
        #                 attrValue = bookInfo.get(attr, '')
        #                 if isinstance(attrValue, list): attrValue = ', '.join(attrValue)
        #                 df.loc[idx, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
        #             updateBuffer(f"Done.")
        
def quitting(df:pd.DataFrame):
    global window
    writeCheckpoint(window.metadata)
    if window.metadata['incomplete']:
        df.to_excel(window.metadata['save_path'], index=False)
        sg.popup(f'Saving checkpoint at {window.metadata["start"]}',title='Close')
    else:
        ckpt_file_path = getCkptPath(window.metadata["input_path"])
        os.remove(ckpt_file_path)


def setElementDisable(disable:bool, *args):
    global window
    for arg in args:
        element = window[arg]
        if isinstance(element, sg.PySimpleGUI.Button):
            element.update(disabled=disable, button_color=conf.BUTTON_APPEARANCE[disable])
        else:
            element.update(disabled=disable)

def main():
    global window, df
    while True:
        event, value = window.read(timeout=10)
        if event == 'Goodbye' or event == sg.WINDOW_CLOSED:
            quitting(df)
            break
        if event == '-File-':
            window.metadata['input_path'] = value['-File-']
            df = pd.read_excel(value['-File-'], sheet_name=conf.SHEET_INDEX)
            readCheckpoint(window.metadata) # what should be updated: th
            window.metadata['end'] = len(df.index)
            window['-Prog-'].update(current_count=window.metadata['start'], max=window.metadata['end'])
            setElementDisable(False, '-Reset-', '-Toggle-', '-Preview-', '-Save-', '-Add-')
            updateBuffer(f'Saving result to {window.metadata["save_path"]}.')
        if event == '-Toggle-':
            setElementDisable(True, '-Add-')
            window.metadata['append'] = value['-Add-'] # unnecessary?
            if (f'{df.columns[0]}{conf.FOUND_ATTRIBUTE_POSTFIX}' in df.columns) != window.metadata['append']:
                foundAttrName = [i + conf.FOUND_ATTRIBUTE_POSTFIX for i in conf.EXCEL_FIELDS]
                if window.metadata['append']:
                    df = pd.concat([df, pd.DataFrame(columns=foundAttrName)])
                else:
                    df = df.drop(foundAttrName, axis=1)
            window.metadata['process'] = not(window.metadata['process'])
            setElementDisable(window.metadata['process'], '-Reset-', '-Preview-', '-Save-')
            window['-Toggle-'].update(text = 'Pause' if window.metadata['process'] else 'Start')
        if event == '-Reset-':
            setElementDisable(False, '-Toggle-')
            window['-Toggle-'].update(text='start')
            updateBuffer('Resetted progress', clear=True)
            window.metadata['start'] = 0
            window['-Prog-'].update(current_count=0)
            window['-Add-'].update(disabled=False)
            window.metadata['incomplete'] = True
            if (f'{df.columns[0]}{conf.FOUND_ATTRIBUTE_POSTFIX}') in df.columns:
                keep_cols = [_ for _ in df.columns if not(_.endswith(conf.FOUND_ATTRIBUTE_POSTFIX))]
                df = pd.DataFrame(df[keep_cols], columns=df.columns)
            # writeCheckpoint(window.metadata)
        if event == '-Preview-':
            preview(df)
        if event == 'Save As':
            window.metadata['save_path'] = value['-Save-']
            updateBuffer(f'Now saving to {window.metadata["save_path"]}')
        process(df)
        window['-Log-'].update(value=conf.GUILogger.buffer)
    window.close()

df = None
os.makedirs(f'{os.getcwd()}/.tmp', exist_ok=True)
window = createMainWindow()

if __name__ == '__main__':
    main()