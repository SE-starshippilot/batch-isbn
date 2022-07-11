import re
import json
import numpy as np

import config as conf
from utils import strMatch, truncate

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