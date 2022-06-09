import json
import numpy as np
from fuzzywuzzy import fuzz, process
from difflib import SequenceMatcher
from functools import partial, reduce

conf = None

def calcRecordSimilarity(correct:dict, found:list)->int:
    """
        Calculate the similarity between a given record and the correct, return the information found and a heuristic similarity
    """

    def calcAttrSimilarity(attribute_name: str) -> list:
        """
            returns the similarity ratio of best match between the correct and found content on a given attribute
            0 means not found, 1 means found exact, decimal means fuzzy
        """
        correctAttr = correct[attribute_name]
        foundAttr = found[attribute_name]

        if isinstance(correctAttr, int): # For publish year, there could be only one possible value
            diff = np.clip(np.array(foundAttr) - correctAttr, -2, 2)
            similarity = (2 - min(np.absolute(diff)))/2
            year = -1
            if similarity == 1:
                year = correctAttr
            elif similarity != 0:
                year = correctAttr + 1 if np.absolute(diff) == np.max(diff) else correctAttr - 1
            return year, (2 - min(diff))/2 # 0 if no match, 0.5 ± 1, 1 exact match
        
        if not(isinstance(correctAttr, list)): # For publisher and author, for code simplicity, transfer single-valued string to list
            correctAttr = [correctAttr]
        if not(isinstance(foundAttr, list)):
            foundAttr = [foundAttr]

        matchRatio = np.zeros(len(correctAttr))
        matchNames = []
        for _ in enumerate(correctAttr):
            name, score = strMatch(_[1], foundAttr)
            matchRatio[_[0]] = score
            matchNames.append(name)
        return matchNames, np.average(matchRatio)

    recordSimilarity = 0
    recordInfo = {}
    for _, attribute in enumerate(conf['ATTRIBUTES']):
        attrInfo, attrSimiarity = calcAttrSimilarity(attribute)
        recordSimilarity = recordSimilarity * 10 + attrSimiarity
        recordInfo[attribute] = attrInfo
    return recordInfo, recordSimilarity

def strMatch(correct: str, found: list) -> list:
    """
    returns the most similar string in found and the similarity index
    it is also possible that the substring of the correct string has higher similarity
    e.g: correct is 'WLC Books' and there is 'W L C' in found. They should be the most similar one.
    """
    subCorrect = correct.split(' ')
    subCorrect.append(correct)
    maxSub = (None, -1)
    for sub in subCorrect:
        res = process.extractOne(correct, found , scorer=fuzz.partial_ratio)
        score = 0 if res[1] < conf['LOWBOUND'] else 1 if res[1] > conf['HIGHBOUND'] else res[1]
        if score > maxSub[1]: maxSub = (res[0], score)
    return maxSub

def getMostSimilarRecord(correct:json, records: list) -> json:
    maxSimilarity = (None, 0)
    for _ in records:
        currSimilarity = calcRecordSimilarity(correct, _)
        if currSimilarity[1] > maxSimilarity[1]:
            maxSimilarity = currSimilarity
    return maxSimilarity[0]

def debug():
    global conf
    with open('config.json') as c:
        conf = json.load(c)
    with open('sample.json', 'r') as f:
        docs = json.load(f)            
        correct = {'title': 'The Elements of Styles',
                'author_name':['William Jr. Struck', 'James McGill'],
                'publish_year': 2009,
                'publisher_facet': 'WLC Books',
                }
        for key in docs.keys():
            if isinstance(docs[key], list):
                print(f'{key} length is {len(docs[key])}')
        # getMostSimilarRecord(correct, docs)

if __name__ == '__main__':
    debug()