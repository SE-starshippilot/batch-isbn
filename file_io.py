import os
import traceback
import json
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename
import config as conf
from config import GUILogger


def getInputDir(fileName: str)->str:
    """
    Ask user for the excel file for processing. Returns absolute path to the file.
    """
    while True:
        try:
            root = tk.Tk()
            root.withdraw()
            if fileName:
                fileDir = fileName
            else:
                fileDir = askopenfilename(
                    title = 'Select the Excel file to process',
                    filetypes=[("Excel files", "*.xlsx *.xls")]
                )
                root.destroy()
            if not(os.path.exists(fileDir)):
                raise NameError
        except NameError:
            tk.messagebox.showerror(
                title = 'Error', 
                message = 'You have not selected a valid file.'
            )
            fileName = None
        else:
            return fileDir

def importData(inputFileName:str, addColumn:bool)->pd.DataFrame:
    df = pd.read_excel(inputFileName, sheet_name=conf.SHEET_INDEX)
    if 'Notes' not in df:
        df['Notes'] = ''
    if addColumn:
        for attr in conf.EXCEL_FIELDS:
            foundAttrName = attr + conf.FOUND_ATTRIBUTE_POSTFIX
            if not(foundAttrName in df.columns):
                df[attr + conf.FOUND_ATTRIBUTE_POSTFIX] = ''
    return df


def readCheckpoint(attr_dict:dict)->dict:
    """
    Read the checkpoint file and return the index of the latest modified item.
    A checkpoint file will be generated if it's absent
    """
    attr_dict['index'] = 0
    ckpt_file_name = f"{attr_dict['-File-'][:attr_dict['-File-'].rfind('.')]}_ckpt.json"
    if not(os.path.exists(ckpt_file_name)):
        updateBuffer(f'Generating checkpoint for file{attr_dict["-File-"]}')
        writeCheckpoint(attr_dict)
    else:
        with open(ckpt_file_name, 'r') as f:
            read_dict = json.load(f)
            try:
                attr_dict['index'] = read_dict['index']
                updateBuffer(f"Restored checkpoint at {attr_dict['index']}")
            except Exception:
                traceback.print_exc()
                updateBuffer('Corrupted checkpoint file. Resetting to 0.')
                writeCheckpoint(attr_dict)
    return attr_dict        

def writeCheckpoint(attr_dict:dict)->None:
    """
    Write the checkpoint attribute as a json file for possible restoration.
    """
    ckpt_file_name = f"{attr_dict['-File-'][:attr_dict['-File-'].rfind('.')]}_ckpt.json"
    with open(ckpt_file_name, 'w') as f:
        json.dump(attr_dict, f)

def updateBuffer(message):
    GUILogger.buffer += f'{message}\n'

def debug():
    f = '/Users/shitianhao/Documents/lib work/LibGuides Spring 2022.xls'
    df = pd.read_excel(f)

if __name__ == '__main__':
    debug()