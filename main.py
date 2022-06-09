import json
import argparse
import pandas as pd
from process import *
from file_io import *

# parser = argparse.ArgumentParser()
# parser.add_argument()
conf = None
colmap = {}

def main():
    global conf
    with open('config.json') as c:
        conf = json.load(c)
    fName = getFilePath(useGUI=True)
    df = pd.read_excel(fName, sheet_name=conf['SHEETINDEX'])

    for attr in conf['ATTRIBUTES']:
        pass


    
def debug():
    main()

if __name__ == '__main__':
    debug()