import xlrd
import json
import pandas as pd
import tkinter as tk
from tkinter.filedialog import askopenfilename

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

def debug():
    f = getFilePath(useGUI = True)
    print(f)

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