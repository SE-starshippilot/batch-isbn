import re
import json
import logging
import argparse
import numpy as np
import pandas as pd

import config as conf
from fuzzywuzzy import fuzz

class AutomateError(Exception):
    def __init__(self, message: str, *args: object) -> None:
        logging.error(message)

truncate = lambda x: 1 if x >= conf.HIGHBOUND else 0 if x <= conf.LOWBOUND else x

convert = lambda attr: conf.EXCEL_FIELD_MAP[attr]

def strMatch(found: str, correct: str) -> float:
    """
    returns maximum similarity index of a given st
    it is also possible that the substring of the correct string has higher similarity
    e.g: correct is 'WLC Books' and there is 'W L C' in found. They should be the most similar one.
    """
    found = found.replace(' ', '')
    subCorrect = correct.split(' ')
    if not(correct in subCorrect): subCorrect.append(correct)
    maxScore = -1
    for sub in subCorrect:
        score = fuzz.partial_ratio(sub, found)/100
        if score > maxScore: maxScore = score
        if maxScore >= conf.MAX_SCORE: break
    return maxScore

strMatchv0 = lambda found, correct: fuzz.partial_ratio(found, correct)/100

def calcEditionSimilarity(found:dict, correct:dict)->int:
    """
        Calculate the similarity between a given edition and the correct, return the information found and a heuristic similarity
        The similarity is based on the publisher, publish date and type of meida
    """
    editionInfo = {'ISBN':['ISBN Not Found']}
    similarityMap = np.zeros_like(conf.HEURISTIC_SCORE_MAP)

    for idx, attr in enumerate(conf.EDITION_ATTRIBUTES):
        foundAttr = found.get(attr, None)
        if foundAttr: # If the record contains attribute
            if idx < 2: # publisher, publish date
                editionInfo[attr] = foundAttr
                correctAttr = correct[conf.QUERY_2_EXCEL[attr]]
                if idx == 0: # publisher
                    similarityMap[idx] = fuzz.partial_ratio(foundAttr, correctAttr)/100
                else: # publish date
                    foundAttr = int(re.findall(conf.YEAR_PATTERN, foundAttr)[0]) # excel reads year as string
                    if correctAttr == foundAttr:
                        similarityMap[idx] = 1
                    elif abs(correctAttr - foundAttr) <= 1:
                        similarityMap[idx] = 0.5
                    else:
                        similarityMap[idx] = 0
            elif idx == 2: # format
                similarityMap[idx] = conf.PHYSICAL_FORMAT_MAP.get(foundAttr, 0)
                editionInfo[attr] = foundAttr
            else: # try to get ISBN. ISBN-13 is preferred.
                editionInfo['ISBN'] = foundAttr[0]
                break
        elif idx < 3:
            similarityMap[idx] = 0

    editionSimilarity = np.array(conf.HEURISTIC_SCORE_MAP) @ similarityMap
    return editionInfo, editionSimilarity

def generateManualURL(bookName:str)->str:
    hasChineseChar = lambda x: len(re.findall(r'[\u4e00-\u9fff]+', x)) != 0
    carrier = conf.CHINESE_BOOK_SEARCH_URL if hasChineseChar(bookName) else conf.ENGLISH_BOOK_SEARCH_URL
    return carrier + bookName

def isWrongInfo(found:any, correct:any)->bool:
    if isinstance(found, str):
        return fuzz.partial_ratio(found, correct)/100 < conf.HIGHBOUND
    elif isinstance(found, list):
        if isinstance(correct, str):
            correct = correct.split(',')
            correct = [x.strip() for x in correct]
        for foundStr in found:
            isContained = lambda x: fuzz.partial_ratio(foundStr, x)/100
            containedList = np.array(list(map(isContained, correct)))
            if any(containedList>conf.HIGHBOUND):
                return False
        return True

def configparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type = str, help='Specify the input file. Specifying this argument will disable GUI.')
    parser.add_argument('-o', '--out', type = str, help='Specify the output file. Not specifying this argument will overwrite existing file.')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'Show details when running. Default not shown.')
    parser.add_argument('-a', '--addColumns', action='store_true', help='Append the found attributes to the file. Default not added.')
    return parser.parse_args()

def configlogger(verbose:bool):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler('experiment.log')
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    if verbose:
        ch.setLevel(logging.INFO) 
    else:
        ch.setLevel(logging.WARNING)

    fmt = logging.Formatter('%(asctime)s [%(levelname)s]:%(message)s')

    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def debug():
    global conf
    lista = ['abc', 'def', 'ghi']
    listb = ['zmk', 'zzz', 'kas']
    print(isWrongInfo(lista, listb))

if __name__ == '__main__':
    debug()