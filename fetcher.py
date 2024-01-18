from scrapper import PageScrapper
from provider import Douban, Amazon, Provider

class ISBNRetriever:
    def __init__(self)->None:
        self.scrapper = PageScrapper()
        self.providers = [Douban(), Amazon()]

    def format_query(self, book_info:dict)->str:
        query = ','.join([book_info['Title'], book_info['Author']])
        return query

    def get_provider(self, book_info:str)->str:
        return self.providers[0] if len(book_info)==1 else self.providers[1]

    def retrieve(self):
        def wrapper(self, provider, url, *args, **kwargs):
            page = self.scrapper.scrap(url)
            if provider.check_antibot(page):
                raise RuntimeError("Anti-bot page detected. Please try again later.")
            response = provider.func(*args)
            return response
        return wrapper
    
    @retrieve
    def get_book_url(self, provider:Provider, book_info:str)->str:
        return provider.get_match_url(book_info)
    
    @retrieve
    def get_book_meta(self, provider:Provider, book_record_url:str)->str:
        return provider.retrieve_metadata(book_record_url)

    def __call__(self, book_info:str)->dict:
        provider = self.get_provider(book_info)
        book_query = self.format_query(book_info)

        best_match_url = self.get_book_url(provider, book_query)
        metadata = self.get_book_meta(provider, best_match_url)

        return metadata