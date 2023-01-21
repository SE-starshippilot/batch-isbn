import os
import time
import pickle
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from bs4 import BeautifulSoup


def retrieve_metadata(url):
    global webdriver
    metadata_dict = {}
    if url: 
        soup = get_source(url)
        metadata = list(soup.find("div", id="info").stripped_strings)
        for idx,token in enumerate(metadata):
            if token[-1] == ':': 
                if len(token) == 1: metadata[idx-1] += metadata.pop(idx)
            elif token == "/":
                metadata[idx-1] += metadata.pop(idx)
                metadata[idx-1] += metadata.pop(idx)
        assert len(metadata) % 2 == 0
        for field in range(0, len(metadata), 2):
            metadata_dict[metadata[field][:-1]] = metadata[field + 1]
    return metadata_dict

def get_source(url):
    global driver
    driver.get(url)
    time.sleep(sleep_interval)
    return BeautifulSoup(driver.page_source, "lxml")

def query_douban(book_info):
    base_url = "https://search.douban.com/book/subject_search?search_text="
    soup = get_source(base_url + book_info)
    bestmatch_book = soup.find("a", class_="title-text")
    return bestmatch_book["href"] if bestmatch_book else None

def add_metadata(metadata_dict):
    global metadata_sum
    for key in metadata_sum.keys():
        if key != "URL": metadata_sum[key].append(metadata_dict.get(key, "N/A"))

# Step 0: Initialize
driver = webdriver.Edge()
ckpt_file = "temp.pkl"
sleep_interval = 0.5
sheet = pd.read_excel("香港史课程推荐购买书目.xlsx")
book_list = sheet["书籍信息"].tolist()
metadata_sum = {"作者": [], "出版社": [], "出版年": [], "ISBN": [], "URL": []}
pbar = tqdm(total=len(book_list))

# Step 1: Query and get best match work
pbar.set_description(f"Fetching book URL...")
if os.path.exists(ckpt_file):
    with open(ckpt_file, "rb") as f:
        metadata_sum = pickle.load(f)
    pbar.update(len(metadata_sum["URL"]))
else:
    for book_info in book_list:
        pbar.update(1)
        url = query_douban(book_info)
        metadata_sum["URL"].append(url)
    with open(ckpt_file, "wb") as f:
        pickle.dump(metadata_sum, f)
pbar.reset()

# Step 2: Retrieve metadata
pbar.set_description(f"Fetching ISBN...")
for url in metadata_sum["URL"]:
    add_metadata(retrieve_metadata(url))
    pbar.update(1)
pbar.close()
driver.close()

# Step 3: Save to Excel
for key in metadata_sum.keys():
    sheet[key] = metadata_sum[key]
sheet.to_excel("香港史课程推荐购买书目_Retrieved_V2.xlsx", index=False)