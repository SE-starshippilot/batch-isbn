import re
import time
import random
from selenium import webdriver
from bs4 import BeautifulSoup

class PageScrapper:
    """
    A class that scrapes a webpage and returns a BeautifulSoup object.
    """
    def __init__(self, min_sleep_interval:float=2.0, max_sleep_interval:float=8.0, trial_times:int=3)->None:
        self.trial_times = trial_times
        self.sleep_interval = lambda : time.sleep(random.random()*(max_sleep_interval - min_sleep_interval) + min_sleep_interval)

    def get_source(self)->BeautifulSoup:
        if self.url is None: return None
        for _ in range(self.trial_times):
            self.sleep_interval()
            self.driver.get(self.url) 
            self.sleep_interval()
            self.driver.execute_script(f"window.scrollTo(0, {random.randrange(0, 1000, 1)});")
            state = self.driver.execute_script("return document.readyState")
            if not(state == "complete"): continue
            response = BeautifulSoup(self.driver.page_source, "lxml")
            return response
        raise RuntimeError("Failed to get source from " + self.url)

    def __enter__(self):
        self.driver = webdriver.Edge()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()
        if exc_type is not None:
            print(exc_type, exc_value, traceback)
            return False
        return True

class Provider:
    
    driver = webdriver.Edge()
    
    def __init__(self, baseURL:str, min_sleep_interval:float=2.0, max_sleep_interval:float=8.0, trial_times:int=3)->None:
        self.baseURL = baseURL
        self.trial_times = trial_times
        self.sleep_interval = lambda : time.sleep(random.random()*(max_sleep_interval - min_sleep_interval) + min_sleep_interval)

    def get_source(self, url:str)->BeautifulSoup:
        if url is None: return None
        for _ in range(self.trial_times):
            self.sleep_interval()
            self.__class__.driver.get(url) 
            self.sleep_interval()
            self.__class__.driver.execute_script(f"window.scrollTo(0, {random.randrange(0, 1000, 1)});")
            state = self.__class__.driver.execute_script("return document.readyState")
            if not(state == "complete"): continue
            response = BeautifulSoup(self.__class__.driver.page_source, "lxml")
            return response
        raise RuntimeError("Failed to get source from " + url)

    def get_match_url(self, page:BeautifulSoup)->str:
        """
        Search for entries within the provider DB, return URL of best matched.
        To be overwritten by subclass
        """        
        raise NotImplementedError

    def check_antibot(self, response:BeautifulSoup)->bool:
        """
        Check if the response is an anti-bot page.
        To be overriden by subclasses.
        """
        return False
    
    def retrieve_metadata(self, response:BeautifulSoup)->dict:
        """
        Retrieve book's metadata from the URL.
        This superclass method must be called in each subclass's overriden methods
        since each provider's result page is different.
        """
        raise NotImplementedError

    def __call__(self, book_info:str)->dict:
        # global logger
        metadata = {}
        book_search_url = self.baseURL + book_info
        metadata['Search URL'] = book_search_url

        # logger.debug(f'Searching at URL {book_search_url}...')
        book_search_page = self.get_source(book_search_url)
        if self.check_antibot(book_search_page):
            raise RuntimeError("Anti-bot page detected. Please try again later.")
        best_match_url = self.get_match_url(book_search_page)

        # logger.debug(f'Best Match URL: {best_match_url}')
        best_match_page = self.get_source(best_match_url)
        if self.check_antibot(book_search_page):
            raise RuntimeError("Anti-bot page detected. Please try again later.")
        metadata.update(self.retrieve_metadata(best_match_page))
        return metadata
    
    def __del__(self):
        self.driver.quit()

class Douban(Provider):
    def __init__(self):
        super().__init__(baseURL="https://search.douban.com/book/subject_search?search_text=")
        self.translation = {
            '作者': 'Fetched Author',
            '出版社': 'Fetched Publisher',
            '出版年': 'Fetched Edition Date',
            'ISBN': 'ISBN',
        }
    
    def __process_token(self, raw_metadata:list) -> dict:
        idx = 0
        is_attr = True
        curr_attr = ''
        curr_value = ''
        final_metadata = {}
        while idx < len(raw_metadata):
            # iterate over the list of tokens, get attr-value pairs
            if is_attr:
                curr_attr += raw_metadata[idx]
                if not(curr_attr.endswith(":")):
                    assert raw_metadata[idx+1].endswith(":")
                    # occasioanlly the comma and the attr is separated
                else:
                    is_attr = False
            else:
                curr_value += raw_metadata[idx]
                # there could be multiple values for a attribute
                if (idx == len(raw_metadata) - 1) or (idx != len(raw_metadata) - 1 and raw_metadata[idx+1] != '/'): # TODO: maybe change to regex expression later
                    is_attr = True
                    curr_attr = curr_attr[:-1]
                    if curr_value.endswith('/'):
                        curr_value = curr_value[:-1] 
                    if curr_attr in self.translation.keys():
                        final_metadata[self.translation[curr_attr]] = curr_value
                    curr_attr = ''
                    curr_value = ''
                else:
                    curr_value += '/'
                    idx += 1
            idx += 1
        return final_metadata

    
    def get_match_url(self, book_search_page:BeautifulSoup) -> str:
        first_match = book_search_page.find("a", class_="title-text", attrs={"data-moreurl": True})
        return first_match['href'] if first_match else None

    def retrieve_metadata(self, book_page:BeautifulSoup) -> dict:
        final_metadata = {}
        final_metadata['Fetched Title'] = book_page.find("a", class_="nbg")["title"]
        raw_metadata = list(book_page.find("div", id="info").stripped_strings)
        # the section of the page containing metadata
        final_metadata.update(self.__process_token(raw_metadata))
        return final_metadata
    
class Amazon(Provider):
    def __init__(self):
        super().__init__(baseURL="https://www.amazon.com/s?k=")

    def get_match_url(self, response:BeautifulSoup) -> str:
        first_match = response.select_one('h2.a-size-mini.a-spacing-none.a-color-base.s-line-clamp-2 > a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
        match_url = self.baseURL.replace("/s?k=", "") + first_match['href'] if first_match else None
        return  match_url

    def __process_token(self, token:str)->str:
        token = token.text.encode('ascii', 'ignore').decode('ascii') # remove any non-ascii characters
        token = token.replace('\n', '').replace('\t', '') # remove line breaks and tabs
        token = re.sub('\s+', ' ', token) # remove extra spaces
        token = token.strip() # remove leading and trailing spaces
        return token


    def retrieve_metadata(self, response:BeautifulSoup) -> dict:
        meta_dict = {}
        title = response.select_one('span#productTitle').get_text(strip=True)
        authors = response.select('span.author.notFaded > a')
        miscs = response.select('div#detailBullets_feature_div > ul > li')
        authors = ', '.join([author.get_text(strip=True) for author in authors])

        meta_dict['Fetched Title'] = title
        meta_dict['Fetched Authors'] = authors

        for misc in miscs:
            misc = self.__process_token(misc)
            attr, value = misc.split(' : ')
            if attr == 'Publisher':
                if value.count(';') == 0:
                    publisher, edition_date = value.split('(')
                    publisher = publisher.strip()
                    edition_date = edition_date.split(')')[0].strip()
                else:
                    publisher, edition_date = value.split(';')
                    edition_date = edition_date.split('(')[1][:-1]
                meta_dict['Fetched Publisher'] = publisher
                meta_dict['Fetched Edition Date'] = edition_date
            elif attr == 'ISBN-13':
                isbn = value.replace('-', '')
                meta_dict['ISBN'] = isbn
        return meta_dict
    
with PageScrapper() as ps:
    print("Starting")