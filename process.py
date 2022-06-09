import re
import json
import numpy as np
from fuzzywuzzy import fuzz

conf = None

def calcEditionSimilarity(correct:dict, found:dict)->int:
    """
        Calculate the similarity between a given edition and the correct, return the information found and a heuristic similarity
        The similarity is based on the publisher, publish date and type of meida
    """
    truncate = lambda x: 1 if x > conf['HIGHBOUND'] else 0 if x < conf['LOWBOUND'] else x

    editionInfo = {}
    attrNum = len(conf['EDITION_ATTRIBUTES'])
    nullMap = np.geomspace(10 ** (attrNum - 1), 1, num=attrNum)
    similarityMap = np.zeros_like(nullMap)
    for idx, attr in enumerate(conf['EDITION_ATTRIBUTES']):
        if attr in found.keys():
            if idx == 0: # search for publisher
                attrInfo = found[attr][0]
                attrSimilarity = strMatch(correct[attr], attrInfo)
            elif idx == 1: # search for publish date
                attrInfo = int(re.findall(conf['YEAR_PATTERN'], found[attr])[0])
                attrSimilarity = 1/ (1 + abs(attrInfo - correct[attr]))
            elif idx == 2: # search for physical format
                attrInfo = found[attr].lower()
                attrSimilarity = conf['PHYSICAL_FORMAT_MAP'].get(attrInfo, 0)
            else:
                attrInfo = found[attr]
                attrSimilarity = 0 # dummy. No real meaning.
            editionInfo[attr] = attrInfo
            similarityMap[idx] = truncate(attrSimilarity)
        else:
            nullMap[idx] = 0

    editionSimilarity = nullMap @ similarityMap
    if conf['EDITION_ATTRIBUTES'][-1] not in editionInfo:
        editionInfo[conf['EDITION_ATTRIBUTES'][-1]] = 'ISBN Not Found'
    return editionInfo, editionSimilarity

def strMatch(correct: str, found: str) -> list:
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

def debug():
    global conf
    with open('config.json') as c:
        conf = json.load(c)
    with open('sampleEditionInfo.json', 'r') as f:
        docs = json.load(f)            
        correct = {
                'publish_date': 2009,
                'publishers': 'WLC Books',
                }
        calcEditionSimilarity(correct, docs)

if __name__ == '__main__':
    debug()