FOUND_ATTRIBUTE_POSTFIX = "_found"
EDITION_ATTRIBUTES = ["publishers", "publish_date", "physical_format", "isbn_13", "isbn_10"]
EXCEL_FIELDS = ["Title", "Author", "Publisher", "Edition Date"]
QUERY_FIELDS = ["title", "author_name"]
QUERY_2_EXCEL = {
    "title": "Title",
    "author_name": "Author",
    "publishers": "Publisher",
    "publish_date": "Edition Date"
}
EXCEL_2_QUERY = {
    "Title": "title",
    "Author": "author_name",
    "Publisher": "publishers",
    "Edition Date": "publish_date"
}
SHEET_INDEX = 0
LOWBOUND = 0.4
HIGHBOUND = 0.7
MAX_SCORE = 1.0
DEBUG = (0, 'DEBUG', 'black')
INFO = (10,'INFO', 'black')
WARNING = (20,'WARNING', 'orange')
ERROR = (30,'ERROR', 'red')
LOG_LEVEL = WARNING
LOG_DICT = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARNING': WARNING,
    'ERROR': ERROR
}
BOOK_QUERY_URL = "https://openlibrary.org/search.json?q="
EDITION_QUERY_URL = "https://openlibrary.org/books/"
ENGLISH_BOOK_SEARCH_PROVIDERS = {"Amazon": "https://www.amazon.com/s?k="}
CHINESE_BOOK_SEARCH_PROVIDERS = {"豆瓣": "https://search.douban.com/book/subject_search?search_text="}
MAXIMUM_TRIALS = 3
YEAR_PATTERN = "[0-9]{4}"
HEURISTIC_SCORE_MAP = [100, 10, 1]
PHYSICAL_FORMAT_MAP={
    "paperback": 1,
    "mass market paperback": 0.8,
    "hardcover": 0.2
}
BUTTON_APPEARANCE = {True:('black', 'grey'), False:('white', '#74b9ff')}
INITIAL_METADICT = {'input_path': '',
                     'save_path':'', 
                     'start': -1, 
                     'end': 0, 
                     'process': False}
G_MESSAGE = ''
class GUILogger():
    buffer = ''
    append = True
window = None
logger = None
english_book_search_url = ENGLISH_BOOK_SEARCH_PROVIDERS["Amazon"]
chinese_book_search_url = CHINESE_BOOK_SEARCH_PROVIDERS["豆瓣"]

