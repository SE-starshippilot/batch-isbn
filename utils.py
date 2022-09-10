import re
import base64
import threading
import traceback
import PySimpleGUI as sg
import numpy as np
from fuzzywuzzy import fuzz

import config as conf

getb64encode = lambda s: base64.b64encode(s.encode("ascii"))

class GUILogger():
    def __init__(self, target: sg.Window, level=conf.INFO):
        self.__target = target
        self.__level = level
    
    def __log(self, level, message, append):
        if level[0] >= self.__level[0]:
            self.__target['-Log-'].update(value=f'[{level[1]}]: {message.rstrip()}\n', append=append, text_color_for_value=level[2])

    def debug(self, message, append=True):
        self.__log(conf.DEBUG, message, append)

    def info(self, message, append=True):
        self.__log(conf.INFO, message, append)

    def warn(self, message, append=True):
        self.__log(conf.WARNING, message, append)
    
    def error(self, message, append=True):
        self.__log(conf.ERROR, message, append)

    def setLevel(self, level):
        self.__level = level

    def __setattr__(self, __name, __value) -> None:
        if __name.endswith('level'):
            assert __value in conf.LOG_DICT.values(), 'Invalid logging level.'
        elif __name.endswith('target'):
            assert isinstance(__value, sg.Window), f'Window {__value} not initialized!'
        else:
            raise ValueError
        self.__dict__[__name] = __value

class AutomateError(Exception):
    def __init__(self,reason:str, *args: object) -> None:
        self.reason = reason
        conf.logger.error(reason)

class MissingInfoError(AutomateError):
    def __init__(self, reason: str, title: str) -> None:
        super().__init__(reason)
        self.__title = title

    def generateManualURL(self)->str:
        hasChineseChar = lambda x: len(re.findall(r'[\u4e00-\u9fff]+', x)) != 0
        carrier = conf.chinese_book_search_url if hasChineseChar(self.__title) else conf.english_book_search_url
        return f'=HYPERLINK("{carrier}{self.__title}", "{self.reason}")'

class NetworkUnreachableError(AutomateError):
    def __init__(self, reason: str, *args: object) -> None:
        super().__init__(reason, *args)

    def __str__(self):
        return 'Network Unreachable'

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

def calcEditionSimilarity(found:dict, correct:dict)->int:
    """
        Calculate the similarity between a given edition and the correct, return the information found and a heuristic similarity
        The similarity is based on the publisher, publish date and type of meida
    """
    editionInfo = {'ISBN': None}
    similarityMap = np.zeros_like(conf.HEURISTIC_SCORE_MAP)

    for idx, attr in enumerate(conf.EDITION_ATTRIBUTES):
        foundAttr = found.get(attr, None)
        if foundAttr: # If the record contains attribute
            if idx < 2: # publisher, publish date
                editionInfo[attr] = foundAttr
                correctAttr = correct[conf.QUERY_2_EXCEL[attr]]
                if idx == 0: # publisher
                    similarityMap[idx] = fuzz.partial_ratio(foundAttr, correctAttr)/100
                else: # publish date: if found > +-1 set to 0
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

def isWrongInfo(found:any, correct:any)->bool:
    def splitAttr(attr:any)->list:
        if isinstance(attr, str):
            attr = attr.split(',')
        attr = [_.strip() for _ in attr]
        return attr
    found, correct = splitAttr(found), splitAttr(correct)
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

if __name__ == '__main__':
    debug()