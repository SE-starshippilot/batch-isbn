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
LOGGING_CONFIGURE = {
    "version" : 1,
    "root" : {
        "handlers" : ["console", "file"],
        "level" : "INFO"
    },
    "handlers" : {
        "console" : {
            "class" : "logging.StreamHandler",
            "stream"  : "ext://sys.stdout",
            "formatter" : "fmt",
            "level" : "WARNING"
        },
        "file" : {
            "class" : "logging.FileHandler",
            "filename" : "access-file.log",
            "formatter" : "fmt",
            "mode" : "w"
        }
    },
    "formatters" : {
        "fmt" : {
            "format" : "%(asctime)s [%(levelname)s]:%(message)s",
            "datefmt" : "%m-%d %H:%M:%S"
        }
    }
}
CHINESE_BOOK_SEARCH_URL = "https://search.douban.com/book/subject_search?search_text="
ENGLISH_BOOK_SEARCH_URL = "https://www.amazon.com/s?k="
BUTTON_APPEARANCE = {True:{"button_color": "black on grey"}, False:{"button_color": "black on blue"}}
class GUILogger():
    buffer = ''

