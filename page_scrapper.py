
import time
import random
from selenium import webdriver
from bs4 import BeautifulSoup

class PageScrapper:
    """
    A class that scrapes a webpage and returns a BeautifulSoup object.
    """
    def __init__(self, min_sleep_interval:float=1.0, max_sleep_interval:float=4.0, trial_times:int=3)->None:
        self.__trial_times = trial_times
        self.__sleep_interval = lambda : time.sleep(random.random()*(max_sleep_interval - min_sleep_interval) + min_sleep_interval)
        self.__driver = webdriver.Edge()

    def scrap(self, url:str)->BeautifulSoup:
        assert isinstance(url, str), "URL must be a string"
        for _ in range(self.__trial_times):
            self.__sleep_interval()
            self.__driver.get(url) 
            self.__driver.execute_script(f"window.scrollTo(0, {random.randrange(0, 1000, 1)});")
            state = self.__driver.execute_script("return document.readyState")
            if not(state == "complete"): continue
            response = BeautifulSoup(self.__driver.page_source, "lxml")
            return response
        raise RuntimeError("Failed to get source from " + url)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.quit()
        if exc_type is not None:
            print(exc_type, exc_value, traceback)
            return False
        return True
    
    def quit(self):
       self.__driver.quit() 

