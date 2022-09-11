import json
import pandas as pd
import PySimpleGUI as sg
from functools import wraps

from query import *
from file_io import *
from utils import *
import config as conf
        
def createMainWindow():
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
        [
            sg.Checkbox(
                text='add retrived info', key='-Append-', disabled=True
            ),
            sg.Text(
                text='output verbosity'
            ),
            sg.OptionMenu(
                values=('DEBUG', 'INFO', 'WARNING', 'ERROR'), default_value='INFO', key='-Level-', disabled=True
            )
        ],
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
    return sg.Window(title=f'Batch ISBN Retriver v{conf.VERSION}', layout=layout, modal=False, metadata=conf.INITIAL_METADICT, icon=r'config\favicon.ico')

def modalize(window_func):
    """
    Disable the buttons on the main window so that only one function is active.
    """
    @wraps(window_func)
    def wrap_window(*args, **kwargs):
            setElementDisable(conf.window, True, '-Preview-', '-Toggle-', '-Reset-', '-Save-', '-Path-')
            window_func(*args, **kwargs)
            setElementDisable(conf.window, False, '-Preview-', '-Toggle-', '-Reset-', '-Save-', '-Path-')
    return wrap_window

@modalize
def preview(df:pd.DataFrame):
    df_headings = list(df.columns)
    df_vals = df.loc[1:, :].fillna('')
    df_vals = df_vals.values.tolist()
    layout = [[sg.Table(headings=df_headings, values=df_vals)]]
    preview_window = sg.Window('Preview', layout, modal=True, icon=r'config\favicon.ico')
    while True:
        event, _ = preview_window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
    preview_window.close()

def process():
    global df
    curr_index = conf.window.metadata['start'] + 1
    conf.window['-Prog-'].update(current_count=curr_index)
    print(f'Starting at {conf.window.metadata["start"]} ending at {conf.window.metadata["end"]}')
    currentRow = df.loc[curr_index, :]
    conf.logger.info(f'Handling Book: {df.loc[curr_index, "Title"]}')
    if currentRow['ISBN'] == currentRow['ISBN']: # the ISBN field is not empty
        df.loc[curr_index, 'Notes'] = 'Found ISBN'
        conf.logger.debug('ISBN already written. Skipping.')
    else:
        if isinstance(currentRow['Notes'], str) and currentRow['Notes'].startswith('Network'):
            currentRow['Notes'] = ''
        bookInfo = None
        try:
            bookInfo = getBookInfo(currentRow)
        except MissingInfoError as me:
            df.loc[curr_index, 'Notes'] = me.generateManualURL()
        except NetworkUnreachableError as ne:
            df.loc[curr_index, 'Notes'] = ne.__str__()
        else:
            conf.logger.info(f"Found ISBN: {bookInfo['ISBN']}")
            df.loc[curr_index, 'ISBN'] = bookInfo['ISBN']
            df.loc[curr_index, 'Notes'] = 'Found ISBN'
            if conf.window.metadata['append']:
                for attr in conf.EXCEL_FIELDS:
                    attrValue = bookInfo.get(conf.EXCEL_2_QUERY[attr], '')
                    if isinstance(attrValue, list): attrValue = ', '.join(attrValue)
                    df.loc[curr_index, attr+conf.FOUND_ATTRIBUTE_POSTFIX] = attrValue
    conf.window.metadata['start'] = curr_index
    return curr_index >= conf.window.metadata['end']
        
def quitting(df:pd.DataFrame): # checked
    global process_thread
    if df is not None: # have read dataframe
        df.to_excel(conf.window.metadata['save_path'], index=False)
        if process_thread is None or process_thread.get_done_status(): # when quitting, the process is already done
            os.remove(getCkptPath(conf.window.metadata["input_path"]))
        else:
            sg.popup(f'Saving checkpoint at {conf.window.metadata["start"]+1}',title='Close', keep_on_top=True)
            writeCheckpoint(conf.window.metadata)
            process_thread.force_quit()
    else:
        process_thread.force_quit()

def setElementDisable(window, disable:bool, *args): # checked
    """
    Batch enable/disable elements on a given window。
    """
    for arg in args:
        element = window[arg]
        if isinstance(element, sg.PySimpleGUI.Button):
            element.update(disabled=disable, button_color=conf.BUTTON_APPEARANCE[disable])
        else:
            element.update(disabled=disable)

def main():
    global df, process_thread
    init = True
    while True:
        event, value = conf.window.read()
        print(event)
        if event == 'Goodbye' or event == sg.WINDOW_CLOSED:
            quitting(df)
            break
        if event == '-File-':
            if os.path.exists(value['-File-']):
                conf.window.metadata['input_path'] = value['-File-']
                df = pd.read_excel(value['-File-'], sheet_name=conf.SHEET_INDEX) # Need to add try statement
                readCheckpoint(conf.window.metadata) # what should be updated?
                conf.window.metadata['end'] = len(df.index) - 1
                conf.window['-Prog-'].update(current_count=conf.window.metadata['start'], max=conf.window.metadata['end']) # restore progress
                conf.window['-Log-'].update(value=f'Saving result to {conf.window.metadata["save_path"]}.\n', append=True)
                setElementDisable(conf.window, False, '-Reset-', '-Toggle-', '-Preview-', '-Save-', '-Level-') # user can reset
                if conf.window.metadata.get('append', None):
                    conf.window['-Append-'].update(value=conf.window.metadata['append']) # make sure information is always added/not added
                    setElementDisable(conf.window, True, '-Append-') # if the window has started processing, user cannot change the 'Append' attribute
                else:
                    setElementDisable(conf.window, False, '-Append-') # if the window has started processing, user cannot change the 'Append' attribute
        if event == '-Toggle-':
            if init:
                conf.window.metadata['append'] = value['-Append-'] # unnecessary?
                if (f'{conf.EXCEL_FIELDS[0]}{conf.FOUND_ATTRIBUTE_POSTFIX}' in df.columns) != conf.window.metadata['append']:
                    foundAttrName = [i + conf.FOUND_ATTRIBUTE_POSTFIX for i in conf.EXCEL_FIELDS]
                    if conf.window.metadata['append']:
                        conf.logger.info("Writing found information into file")
                        df = pd.concat([df, pd.DataFrame(columns=foundAttrName)])
                    else:
                        conf.logger.info(f"Cleaning found information into file")
                        df = df.drop(foundAttrName, axis=1)
                if process_thread.is_alive() == False:
                    process_thread.run()
                init = False
            conf.logger.setLevel(conf.LOG_DICT[value['-Level-']])
            setElementDisable(conf.window, True, '-Append-') # why did I add this statement? To stop the user from changing once process started
            process_thread.toggle()
            setElementDisable(conf.window, process_thread.get_run_status(), '-Reset-', '-Preview-', '-Save-', '-Level-')
            conf.window['-Toggle-'].update(text = 'Pause' if process_thread.get_run_status() else 'Start')
        if event == '-Reset-':
            init = True
            setElementDisable(conf.window, False, '-Toggle-', '-Append-', '-Level-') # make the 'Start' button clickable
            conf.window['-Toggle-'].update(text='Start')
            conf.window['-Log-'].update(value='Resetted progress\n', append=False)
            conf.window.metadata['start'] = 0
            conf.window['-Prog-'].update(current_count=0)
            if process_thread is None:
                process_thread = PThread(target=process, binding_window=conf.window)
                process_thread.start()
            else:
                process_thread.reset()
        if event == '-Preview-':
            preview(df)
        if event == '-Save_As-':
            if value['-Save-'] is not None:
                conf.window.metadata['save_path'] = value['-Save-']
                conf.logger.info(f'Now saving to {conf.window.metadata["save_path"]}',)
        if event == '-Done-':
            conf.logger.debug('Done')
            sg.popup('All done!', title='Batch ISBN v0.2', keep_on_top=True, icon=r'config\favicon.ico')
            setElementDisable(conf.window, True, '-Toggle-')
            setElementDisable(conf.window, False, '-Reset-', '-Preview-', '-Save-', '-Level-')
    conf.window.close()

# initialize the window
df = None
with open('./config/theme.json', 'r') as f:
    sg.theme_add_new('retro', json.load(f)) 
    sg.theme('retro')
os.makedirs(f'{os.getcwd()}/.tmp', exist_ok=True)
conf.window = createMainWindow()
conf.logger = GUILogger(conf.window, level=conf.INFO)
process_thread = PThread(target=process, binding_window=conf.window)
process_thread.start()

if __name__ == '__main__':
    main()
