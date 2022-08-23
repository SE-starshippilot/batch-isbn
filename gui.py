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
                text='add retrived info', key='-Append-', disabled=True
            )
        ]
    progress_list = [
        [
            sg.Multiline(
                size=(40, 25), enter_submits=False, autoscroll=True, auto_refresh=True, key='-Log-'
            )
        ]
    ]
    file_list = [
        [   
            sg.Text("Select an file"),
            sg.In(
                size=(30, 1), enable_events=True, key='-File-', readonly=True
            ),
            sg.FileBrowse(file_types=[("Excel Files", ".xls .xlsx"),], key='-Path-', button_color=('white', '#74b9ff'))
        ],
        [
            sg.Button(
                button_text='preview', tooltip='preview the document you selected', disabled=True, enable_events=True, key='-Preview-', button_color=('black', 'grey')
            ),
            sg.Button(
                button_text='reset progress', tooltip='reset the checkpoint of this file', disabled=True, enable_events=True, key='-Reset-', button_color=('black', 'grey')
            ),
            sg.In(key='-Save_As-', enable_events=True, visible=False),
            sg.FileSaveAs(
                button_text='save as...', tooltip='preview the document you selected', disabled=True, enable_events=True, key='-Save-', button_color=('black', 'grey'), file_types=(('Excel Files', '.xls .xlsx .csv'),), default_extension='xlsx'
            )
        ],
        checkbox_list,
        [
            sg.ProgressBar(
                size=(25, 30), max_value=100, orientation='h', key='-Prog-'
            ),
            sg.Button(
                button_text='Start', tooltip='begin/halt the process', disabled=True, enable_events=True, key='-Toggle-', button_color=('black', 'grey')
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
    return sg.Window(title='Batch ISBN Retriver v0.3', layout=layout, modal=False, metadata=conf.INITIAL_METADICT)

def modalize(window_func):
    """
    Disable the buttons on the main window so that only one function is active.
    """
    @wraps(window_func)
    def wrap_window(*args, **kwargs):
            setElementDisable(window, True, '-Preview-', '-Toggle-', '-Reset-', '-Save-', '-Path-')
            window_func(*args, **kwargs)
            setElementDisable(window, False, '-Preview-', '-Toggle-', '-Reset-', '-Save-', '-Path-')
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

def process():
    global window, df
    curr_index = window.metadata['start'] + 1
    window['-Prog-'].update(current_count=curr_index)
    # for idx in range(window.metadata['start'], window.metadata['end']):
    #     currentRow = df.loc[idx, :]
    window['-Log-'].update(value=f'{curr_index}\n', append=True)
    time.sleep(0.01)
    window.metadata['start'] = curr_index
    return window.metadata['start'] > window.metadata['end']
        #         window['-Log-'].update(value=f'Handling Book: {df.loc[idx, "Title"]}\n', append=True)
        #         if isinstance(currentRow['ISBN'], str): # the ISBN field is not empty
        #             df.loc[idx, 'Notes'] = 'ISBN already available'
        #             window['-Log-'].update(value='ISBN already written. Skipping.\n', append=True)
        #         else:
        #             if currentRow.isna().sum() > 2: # If fields other than ISBN and Notes are empty
        #                 df.loc[idx, 'Notes'] = generateManualURL(currentRow['Title'])
        #                 window['-Log-'].update(value='\tDetected Missing Fields. Generating URL for manual retrival.\n', append=True)
        #                 continue
        #             else:
        #                 try:
        #                     bookInfo = getBookInfo(currentRow)
        #                 except AutomateError:
        #                     df.loc[idx, 'Notes'] = generateManualURL(currentRow['Title'])
        #                     window['-Log-'].update(value='No matching information found. Generating URL for manual retrival.\n', append=True)
        #                     continue
        #                 else:
        #                     window['-Log-'].update(value=f"Found ISBN: {bookInfo['ISBN']}\n", append=True)
        #                     df.loc[idx, 'ISBN'] = bookInfo['ISBN']
        #         if window.metadata['-Append-']:
        #             window['-Log-'].update(value=f"Writing found information into file...\n", append=True)
        #             for attr in conf.EXCEL_FIELDS:
        #                 attrValue = bookInfo.get(attr, '')
        #                 if isinstance(attrValue, list): attrValue = ', '.join(attrValue)
        #                 df.loc[idx, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
        #             window['-Log-'].update(value=f"Done.\n", append=True)
        
def quitting(df:pd.DataFrame):
    global window
    if process_thread.get_done_status():
        ckpt_file_path = getCkptPath(window.metadata["input_path"])
        os.remove(ckpt_file_path)
    elif df is not None:
            df.to_excel(window.metadata['save_path'], index=False)
            sg.popup(f'Saving checkpoint at {window.metadata["start"]}',title='Close', keep_on_top=True)
            writeCheckpoint(window.metadata)


def setElementDisable(window, disable:bool, *args):
    for arg in args:
        element = window[arg]
        if isinstance(element, sg.PySimpleGUI.Button):
            element.update(disabled=disable, button_color=conf.BUTTON_APPEARANCE[disable])
        else:
            element.update(disabled=disable)

def init_process():
    pass

def main():
    global window, df, process_thread
    init = True
    while True:
        event, value = window.read()
        print(event)
        if event == 'Goodbye' or event == sg.WINDOW_CLOSED:
            process_thread.force_quit()
            quitting(df)
            break
        if event == '-File-':
            if os.path.exists(value['-File-']):
                window.metadata['input_path'] = value['-File-']
                df = pd.read_excel(value['-File-'], sheet_name=conf.SHEET_INDEX) # Need to add try statement
                readCheckpoint(window.metadata) # what should be updated?
                window.metadata['end'] = len(df.index)
                window['-Append-'].update(value=window.metadata['append']) # make sure information is always added/not added
                window['-Prog-'].update(current_count=window.metadata['start'], max=window.metadata['end']) # restore progress
                window['-Log-'].update(value=f'Saving result to {window.metadata["save_path"]}.\n', append=True)
                setElementDisable(window, False, '-Reset-', '-Toggle-', '-Preview-', '-Save-', '-Append-') # user can reset
        if event == '-Toggle-':
            if init:
                # init_process()
                setElementDisable(window, True, '-Append-') # why did I add this statement? To stop the user from changing once process started
                window.metadata['append'] = value['-Append-'] # unnecessary?
                if (f'{df.columns[0]}{conf.FOUND_ATTRIBUTE_POSTFIX}' in df.columns) != window.metadata['append']:
                    foundAttrName = [i + conf.FOUND_ATTRIBUTE_POSTFIX for i in conf.EXCEL_FIELDS]
                    if window.metadata['append']:
                        df = pd.concat([df, pd.DataFrame(columns=foundAttrName)])
                    else:
                        df = df.drop(foundAttrName, axis=1)
                if process_thread.is_alive() == False:
                    process_thread.run()
            process_thread.toggle()
            setElementDisable(window, process_thread.get_run_status(), '-Reset-', '-Preview-', '-Save-')
            window['-Toggle-'].update(text = 'Pause' if process_thread.get_run_status() else 'Start')
        if event == '-Reset-':
            init = True
            setElementDisable(window, False, '-Toggle-', '-Append-') # make the 'Start' button clickable
            window['-Toggle-'].update(text='Start')
            window['-Log-'].update(value='Resetted progress\n', append=False)
            window.metadata['start'] = 0
            window['-Prog-'].update(current_count=0)
            window.metadata['incomplete'] = True # may change after changing to multithreading
            if process_thread is None:
                process_thread = PThread(target=process, binding_window=window)
                process_thread.start()

            # process_thread.reset()
            # if (f'{df.columns[0]}{conf.FOUND_ATTRIBUTE_POSTFIX}') in df.columns: # TODO: check this (do we even need this?)
            #     keep_cols = [_ for _ in df.columns if not(_.endswith(conf.FOUND_ATTRIBUTE_POSTFIX))]
            #     df = pd.DataFrame(df[keep_cols], columns=df.columns)
            # writeCheckpoint(window.metadata)
        if event == '-Preview-':
            preview(df)
        if event == '-Save_As-':
            window.metadata['save_path'] = value['-Save-']
            window['-Log-'].update(value=f'Now saving to {window.metadata["save_path"]}\n', append=True)
        if event == '-Done-':
            window['-Log-'].update(value='Done\n', append=True)
            sg.popup('All done!', title='Batch ISBN v0.2', keep_on_top=True)
            setElementDisable(window, True, '-Toggle-')
            setElementDisable(window, False, '-Reset-', '-Preview-', '-Save-')
            process_thread = None
    window.close()

df = None

sg.theme_add_new('retro', conf.THEME_DICT) 
sg.theme('retro')
os.makedirs(f'{os.getcwd()}/.tmp', exist_ok=True)
window = createMainWindow()
process_thread = PThread(target=process, binding_window=window)
process_thread.start()

if __name__ == '__main__':
    main()
