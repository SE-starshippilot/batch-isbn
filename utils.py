import re

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

truncate = lambda x: 1 if x >= conf.HIGHBOUND else 0 if x <= conf.LOWBOUND else x

hasChineseChar = lambda x: len(re.findall(r'[\u4e00-\u9fff]+', x)) != 0
