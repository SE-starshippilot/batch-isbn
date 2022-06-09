EDITION_ATTRIBUTES = ["publishers", "publish_date", "physical_format", "isbn_13"],
BOOK_ATTRIBUTES =["title", "author_name", "edition_key"],
SHEETINDEX = 0,
LOWBOUND = 0.3,
HIGHBOUND = 0.8,
BOOK_QUERY_URL = "https://openlibrary.org/search.json?title=",
EDITION_QUERY_URL = "https://openlibrary.org/books/",
MAXIMUM_TRIALS = 3,
YEAR_PATTERN = "[0-9]{4}",
PHYSICAL_FORMAT_MAP={
    "paperback": 1,
    "mass market paperback": 0.8,
    "hardcover": 0.2
}