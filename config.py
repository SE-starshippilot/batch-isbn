FOUND_ATTRIBUTE_POSTFIX = "_found"
EDITION_ATTRIBUTES = ["publishers", "publish_date", "physical_format", "isbn_13", "isbn_10"]
EXCEL_FIELDS = ["ISBN", "Title", "Author", "Publisher", "Edition Date"]
QUERY_FIELDS = ["title", "author_name"]
QUERY_2_EXCEL = {
    "title": "Title",
    "author_name": "Author",
    "publishers": "Publisher",
    "publish_date": "Edition Date"
}
SHEET_INDEX = 0
LOWBOUND = 0.4
HIGHBOUND = 0.8
MAX_SCORE = 1.0
BOOK_QUERY_URL = "https://openlibrary.org/search.json?q="
EDITION_QUERY_URL = "https://openlibrary.org/books/"
MAXIMUM_TRIALS = 3
YEAR_PATTERN = "[0-9]{4}"
HEURISTIC_SCORE_MAP = [100, 10, 1]
PHYSICAL_FORMAT_MAP={
    "paperback": 1,
    "mass market paperback": 0.8,
    "hardcover": 0.2
}
CHINESE_BOOK_SEARCH_URL = "https://search.douban.com/book/subject_search?search_text="
ENGLISH_BOOK_SEARCH_URL = "https://www.amazon.com/s?k="
BUTTON_APPEARANCE = {True:('black', 'grey'), False:('white', '#74b9ff')}
INITIAL_METADICT = {'input_path': '',
                     'save_path':'', 
                     'start': -1, 
                     'end': 0, 
                     'process': False, 
                     'append':False}
G_MESSAGE = ''
class GUILogger():
    buffer = ''
    append = True
window = None

