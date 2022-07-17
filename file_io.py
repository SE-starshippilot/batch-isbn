import os
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename
import config as conf

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
    df = pd.read_excel(inputFileName, sheet_name=conf.SHEET_INDEX, usecols=conf.EXCEL_FIELDS)
    if 'Notes' not in df:
        df['Notes'] = ''
    if addColumn:
        for attr in conf.EXCEL_FIELDS:
            foundAttrName = attr + conf.FOUND_ATTRIBUTE_POSTFIX
            if not(foundAttrName in df.columns):
                df[attr + conf.FOUND_ATTRIBUTE_POSTFIX] = ''
    return df


def readCheckpoint()->int:
    """
    Read the checkpoint file and return the index of the latest modified item.
    A checkpoint file will be generated if it's absent
    """
    if not(os.path.exists('ckpt.txt')):
        print('No checkpoint file found, generating...')
        writeCheckpoint(0)
        return 0
    with open('ckpt.txt', 'r') as f:
        return int(f.read())

def writeCheckpoint(index:int)->None:
    with open('ckpt.txt', 'w') as f:
        f.write(str(index))

def debug():
    f = '/Users/shitianhao/Documents/lib work/LibGuides Spring 2022.xls'
    df = pd.read_excel(f)

# def getSheetIndex(file:pd.DataFrame)->int:
    # if len(file.sheet_names) != 1:
    #     try:
    #         idx = input('Please input the index of sheet containing information(default=1)')
    #         if idx:
    #             return int(idx)
    #         else:
    #             return 1
    #     except ValueError
    # return 1

if __name__ == '__main__':
    debug()