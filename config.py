FOUND_ATTRIBUTE_POSTFIX = "_found"
EDITION_ATTRIBUTES = ["publishers", "publish_date", "physical_format", "isbn_10", "isbn_13"]
BOOK_ATTRIBUTES = ["title", "author_name", "edition_key"]
EXCEL_ATTRIBUTES = ["isbn", "title", "author_name", "publish_date", "publishers"]
SHEET_INDEX = 0
LOWBOUND = 0.4
HIGHBOUND = 0.8
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
EXCEL_FIELD_MAP={
    "isbn": 'ISBN',
    "title": 'Title', 
    "author_name": 'Author', 
    "publish_date": 'Edition Date', 
    "publishers": 'Publisher'
}
ERROR_CODE={
    1: "ISBN already available",
    2: "No Information Found",
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
ABORT_INDEX = 227
CHINESE_BOOK_SEARCH_URL = "https://search.douban.com/book/subject_search?search_text="
ENGLISH_BOOK_SEARCH_URL = "https://www.amazon.com/s?k="