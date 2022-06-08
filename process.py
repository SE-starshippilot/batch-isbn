import json
import numpy as np
from functools import partial, reduce
from difflib import SequenceMatcher

LOWBOUND = 0.3          # Any similarity lower than this value will be considered as 0
HIGHBOUND = 0.8         # Any similarity higher than this value will be considered as 1

def calcSimilarity(correct:dict, found:list)->int:
    """
        Calculate the similarity between a given record and the correct, return a heuristic similarity index
    """

    def getAttrSimilarity(attribute_name: str) -> list:
        """
            returns the similarity ratio of best match between the correct and found content on a given attribute
            0 means not found, 1 means found exact, decimal means fuzzy
        """
        global conf
        nonlocal correct, found
        correctAttr = correct[attribute_name]
        foundAttr = found[attribute_name]

        if isinstance(correctAttr, int): # For publish year, there could be only one possible value
            diff = np.clip(np.absolute(np.array(foundAttr) - correctAttr), 0, 2)
            return (2 - min(diff))/2 # 0 if no match, 0.5 ± 1, 1 exact match
        
        if isinstance(foundAttr, str): # For book name, each found record has only one value
            return strMatch(correctAttr, foundAttr)
        
        if not(isinstance(correctAttr, list)): # For publisher and author, for code simplicity, transfer single-valued string to list
            correctAttr = [correctAttr]

        vecStrMatch = np.vectorize(strMatch) # Vectorize the function for calculating string similarity for mapping
        getMostSimilar = lambda item: max(vecStrMatch(item, foundAttr)) # Find the most similar attribute value in a list of values
        vecSim = np.vectorize(getMostSimilar)
        return np.average(vecSim(correctAttr))

    similarityIndex = 0
    for _, attribute in enumerate(conf['ATTRIBUTES']):
        similarityIndex = similarityIndex * 10 + getAttrSimilarity(attribute)
    return similarityIndex

def strMatch(correct: str, found: str) -> int:
    res = SequenceMatcher(lambda x: x in " \t", correct, found).ratio()
    return 0 if res < LOWBOUND else 1 if res > HIGHBOUND else res

def getMostSimilarRecord(correct:json, records: list) -> json:
    maxSimilarity = (0, None)
    for _ in enumerate(records):
        if calcSimilarity(correct, _[1]) > maxSimilarity[0]:
            maxSimilarity = _
    return maxSimilarity[1]
        
# def writeRecord(record: list)

def debug():
    with open('sample.json', 'r') as f:
        docs = json.load(f)            
        correct = {'title': 'The Elements of Styles',
                'author_name':['William Jr. Struck', 'James McGill'],
                'publish_year': 2009,
                'publisher_facet': 'WLC Books',
                }
        e_docs = enumerate(docs)
        []
        for doc in docs:
            calcSimilarity(correct, doc)

if __name__ == '__main__':
    debug()