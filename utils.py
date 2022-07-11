import re
import json
import numpy as np

import config as conf
from fuzzywuzzy import fuzz

def strMatch(found: str, correct: str) -> list:
    """
    returns maximum similarity index of a given st
    it is also possible that the substring of the correct string has higher similarity
    e.g: correct is 'WLC Books' and there is 'W L C' in found. They should be the most similar one.
    """
    found = found.replace(' ', '')
    subCorrect = correct.split(' ')
    subCorrect.append(correct)
    maxScore = -1
    for sub in subCorrect:
        score = fuzz.partial_ratio(sub, found)/100
        if score > maxScore: maxScore = score
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

truncate = lambda x: 1 if x >= conf.HIGHBOUND else 0 if x <= conf.LOWBOUND else x

hasChineseChar = lambda x: len(re.findall(r'[\u4e00-\u9fff]+', x)) != 0

def debug():
    global conf
    with open('sampleEditionInfo.json', 'r') as f:
        docs = json.load(f)            
        correct = {
                'publish_date': 2009,
                'publishers': 'WLC Books',
                }
        calcEditionSimilarity(docs, correct)

if __name__ == '__main__':
    debug()