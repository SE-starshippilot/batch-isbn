import re
import json
import numpy as np
import pandas as pd
from functools import partial

import config as conf
from fuzzywuzzy import fuzz

truncate = lambda x: 1 if x >= conf.HIGHBOUND else 0 if x <= conf.LOWBOUND else x

hasChineseChar = lambda x: len(re.findall(r'[\u4e00-\u9fff]+', x)) != 0

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

def calcEditionSimilarity(found:dict, correct:dict)->int:
    """
        Calculate the similarity between a given edition and the correct, return the information found and a heuristic similarity
        The similarity is based on the publisher, publish date and type of meida
    """

    def calcAttrSimilarity(idx:str, found: any, correct: any=None)->int:
        if idx == 0:
            return truncate(strMatch(found[0], correct))
        elif idx == 1:
            try:
                attrInfo = int(re.findall(conf.YEAR_PATTERN, found)[0])
            except IndexError:
                return 0
            else:
                return 1/ (1 + abs(attrInfo - correct))
        else:
            return conf.PHYSICAL_FORMAT_MAP.get(found, 0)
            
    editionInfo = {'isbn':['ISBN Not Found']}
    similarityMap = np.zeros_like(conf.HEURISTIC_SCORE_MAP)
    for idx, attr in enumerate(conf.EDITION_ATTRIBUTES):
        foundAttr = found.get(attr, None)
        if foundAttr: # If the record contains attribute
            if idx < 2:
                editionInfo[attr] = foundAttr
                correctAttr = correct.get(attr, None)
                if correctAttr: 
                    similarityMap[idx] = calcAttrSimilarity(idx, foundAttr, correctAttr)
            elif idx == 2:
                similarityMap[idx] = calcAttrSimilarity(idx, foundAttr)
                editionInfo[attr] = foundAttr
            else: # try to get ISBN. ISBN-13 is preferred.
                editionInfo[conf.EXCEL_ATTRIBUTES[0]] = foundAttr

    editionSimilarity = np.array(conf.HEURISTIC_SCORE_MAP) @ similarityMap
    return editionInfo, editionSimilarity

def calcMaxSimilarity(correct:dict)->int:
    nullMap = np.ones_like(conf.HEURISTIC_SCORE_MAP)
    for idx, attr in enumerate(conf.EDITION_ATTRIBUTES[:2]):
        nullMap[idx] = attr in correct.keys()
    return nullMap @ np.array(conf.HEURISTIC_SCORE_MAP)

def generateManualURL(bookName:str, carrier:str)->str:
    return carrier + bookName

def parseEdition(row:pd.Series)->dict:
    editionInfo = {}
    for attr in conf.EDITION_ATTRIBUTES[:2]: # publisher and publish_date
        attrInfo = row[convert(attr)]
        if isinstance(attrInfo, str) or not(np.isnan(attrInfo)):
            editionInfo[attr] = attrInfo
    return editionInfo

def parseRow(row:pd.Series)-> dict:
    return row

def initializeMapping(programAttr: list, excelAttr: list)->dict:
    pass

def isWrongInfo(found:any, correct:any)->bool:
    if isinstance(found, str):
        return strMatch(found, correct) > conf.HIGHBOUND
    elif isinstance(found, list):
        for foundStr in found:
            isContained = lambda x: strMatch(foundStr, x)
            containedList = map(isContained, correct)
            if any(containedList) > conf.HIGHBOUND:
                return True
        return False


def debug():
    global conf
    lista = ['abc', 'def', 'ghi']
    listb = ['zmk', 'zzz', 'kas']
    print(isWrongInfo(lista, listb))
    # with open('sampleEditionInfo.json', 'r') as f:
    #     docs = json.load(f)            
    #     correct = {
    #             'publish_date': 2009,
    #             'publishers': 'WLC Books',
    #             }
    #     calcEditionSimilarity(docs, correct)

if __name__ == '__main__':
    debug()