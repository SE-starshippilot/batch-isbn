import logging
import pandas as pd
import PySimpleGUI as sg

from file_io import *

class GUILogger(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def log(self, message):
        global buffer, window
        buffer = f'{buffer}\n{message}'.strip()
        window['-log-'].update(value=buffer)


def createMainWindow():
    file_list = [
        [   
            sg.Text("Select an excel doccument"),
            sg.In(
                size=(50, 1), enable_events=True, key='-File-', 
            ),
            sg.FileBrowse()
        ],
        [
            sg.Output(
                size=(150, 200), key='-log-'
            )
        ]
    ]

    return sg.Window(title='Batch ISBN Retriver v0.1', layout=file_list, size=(800, 600))

def createPreviewWindow(headings, contents):
    # header = [sg.Text(i) for i in heading]
    layout = [[sg.Table(values=contents, headings=headings)]]
    return sg.Window(title='Preview', layout=layout)

def main():
    global lh, window
    window = createMainWindow()
    preview = None
    while True:
        event, value = window.read()
        if event == 'Goodbye' or event == sg.WINDOW_CLOSED:
            break
        if event == '-File-':
            df = importData(value['Browse'], True)
            lh.log('hello')
    window.close()

buffer=''
window=None
lh = GUILogger()

if __name__ == '__main__':
    main()