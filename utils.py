import re
import traceback
import base64
import threading
import PySimpleGUI as sg
import numpy as np
from fuzzywuzzy import fuzz

import config as conf
from config import GUILogger

truncate = lambda x: 1 if x >= conf.HIGHBOUND else 0 if x <= conf.LOWBOUND else x
getb64encode = lambda s: base64.b64encode(s.encode("ascii"))
convert = lambda attr: conf.EXCEL_FIELD_MAP[attr]

class AutomateError(Exception):
    def __init__(self, message: str, *args: object) -> None:
        conf.window['-Log-'].update(value=message, append=True)

class PThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, daemon=None, binding_window=None):
        super().__init__(group=group, target=target, name=name)
        self.__args =  args 
        self.__kwargs =  kwargs
        self.__proc_func = target
        self.__binding_window = binding_window
        self.__running = threading.Event()
        self.__done = threading.Event()
        self.__running.clear()
        self.__done.clear()
        self.__quit = False

    def run(self):
        while True:
            self.__running.wait()
            try:
                if self.__quit == False and self.__proc_func(*self.__args, **self.__kwargs):
                    self.__done.set()
                    self.__quit = True # normal exit
            except:
                print('Something nasty happened')
                self.__quit = True # during the process something fkd up
            finally:
                if self.__quit:            
                    self.__binding_window.write_event_value('-Done-', True) # False means unexpected quitting
                    break
    
    def toggle(self):
        if self.__running.is_set():
            self.__running.clear()
        else:
            self.__running.set()
    
    def force_quit(self):
        print('forced quitting')
        self.__quit = True # the window is closed (forced quit)
        self.__running.set() # unblock the thread even if it's paused to break the loop
        del self.__proc_func, self._args, self._kwargs # should I keep it?

    def reset(self):
        self.__running.clear()
        self.__done.clear()
        self.__quit = False # TODO: is this necessary
    
    def get_done_status(self)->bool:
        return self.__done.is_set()

    def get_run_status(self)->bool:
        return self.__running.is_set()


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

def debug():
    global conf
    lista = ['abc', 'def', 'ghi']
    listb = ['zmk', 'zzz', 'kas']
    print(isWrongInfo(lista, listb))

def updateBuffer(message, append=True):
    assert isinstance(conf.window, sg.Window), 'Window not initialized!'
    stack_length = len(traceback.format_stack())
    print(stack_length)
    # conf.window['-Append-'].update(value=message, append=append)

if __name__ == '__main__':
    debug()