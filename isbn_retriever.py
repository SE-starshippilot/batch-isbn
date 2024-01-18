from page_scrapper import PageScrapper
from service_provider import Douban, Amazon, Provider
from pandas import Series

class ISBNRetriever:
    def __init__(self)->None:
        self.scrapper = PageScrapper()
        self.providers = [Amazon(), Douban(),]

    def format_query(self, provider:Provider, book_info:Series)->str:
        assert 'Title' in book_info and 'Author' in book_info, 'Inconsistent row naming'
        query_string = book_info['Title']  # not sure whether to add more info into query
        # query_string = ' '.join([book_info['Title'], book_info['Author']])
        return provider.baseURL + query_string

    def get_provider(self, book_info:str)->str:
        assert 'Title' in book_info and 'Author'
        return self.providers[0] if book_info['Title'].isascii() else self.providers[1]

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

        best_match_url = self.get_book_url(provider, book_query)
        metadata = self.get_book_meta(provider, best_match_url) if best_match_url else {}
        metadata['Search URL'] = best_match_url

        return metadata
    