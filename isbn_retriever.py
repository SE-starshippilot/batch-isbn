from page_scrapper import PageScrapper
from service_provider import Douban, Amazon, Provider
from pandas import Series
import re

class ISBNRetriever:
    def __init__(self)->None:
        self.scrapper = PageScrapper()
        self.providers = [Amazon(), Douban(),]

    def format_query(self, provider:Provider, book_info:Series)->str:
        assert 'Title' in book_info , 'Inconsistent row naming'
        if 'Author' in book_info:
            query_string = ' '.join([book_info['Title'], book_info['Author']]) # TODO: changing to return different queries based on searching results
        else:
            query_string = book_info['Title']
        return provider.baseURL + query_string

    def get_provider(self, book_info:str)->str:
        assert 'Title' in book_info and 'Author'
        return self.providers[1] if bool(re.search('[\u4e00-\u9fff]', book_info['Title'])) else self.providers[0]

    def retrieve(func):
        """
        This modifier takes in a function with two parameters: the first one is the service provider and the second one is the URL to serve.
        It should be noted that when the function is actually wrapped the value of the second parameter is altered from the URL to the page's source code.
        """
        def wrapper(self, provider, url, *args, **kwargs):
            page = self.scrapper.scrap(url)
            if provider.check_antibot(page):
                raise RuntimeError("Anti-bot page detected. Please try again later.")
            response = func(provider, page, *args, **kwargs)
            return response
        return wrapper
    
    @retrieve
    def get_book_url(provider:Provider, book_info:str)->str:
        return provider.get_match_url(book_info)

    @retrieve
    def get_book_meta(provider:Provider, book_record_url:str)->str:
        return provider.retrieve_metadata(book_record_url)

    def __call__(self, book_info:str)->dict:
        provider = self.get_provider(book_info)
        book_query = self.format_query(provider, book_info)

        urls = self.get_book_url(provider, book_query)
        if len(urls) == 0: 
            return {'Search URL': book_query} # handling empty result (if no urls matches could be found)
        for url in urls:
            try:
                metadata = self.get_book_meta(provider, url) if url else {}
                metadata['Search URL'] = url
                return metadata
            except Exception:
                continue
        return {'Search URL': book_query} # handling empty result (if all the urls visitted cannot be processed)
    
    def quit(self):
        self.scrapper.quit()
    