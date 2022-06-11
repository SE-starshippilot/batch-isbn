import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename
import config as conf

def getFilePath(useGUI = False)->str:
    """
    Ask user for the excel file for processing. Returns absolute path to the file.
    """
    while True:
        try:
            if  useGUI:
                root = tk.Tk()
                root.withdraw()
                dir = askopenfilename(
                    title = 'Select the Excel file to process',
                    filetypes=[("Excel files", "*.xlsx *.xls")]
                )
                root.destroy()
            else: 
                dir = input('Please input path to file:')
            if not(dir):
                raise NameError
        except NameError:
            tk.messagebox.showerror(
                title = 'Error', 
                message = 'You have not selected a window.'
            )
        else:
            return dir

def importData(inputFileName:str)->pd.DataFrame:
    df = pd.read_excel(inputFileName, sheet_name=conf.SHEET_INDEX)
    for attr in conf.EXCEL_ATTRIBUTES:
        foundAttrName = attr + conf.FOUND_ATTRIBUTE_POSTFIX
        if not(foundAttrName in df.columns):
            df[attr + conf.FOUND_ATTRIBUTE_POSTFIX] = ''
    return df

def exportData(inputFileName:str, data:pd.DataFrame, overwrite = False, out_format = None)->None:
    postfixPos = inputFileName.rfind('.')
    if postfixPos == -1:
        raise NameError
    if overwrite:
        data.to_excel(inputFileName, index=False)
    else:
        fileNameNoPostfix = inputFileName[:postfixPos]
        filePostfix = out_format if out_format else inputFileName[postfixPos:]
        outputFileName =  fileNameNoPostfix + '_FOUNDED' + filePostfix
        data.to_excel(outputFileName, index=False)

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