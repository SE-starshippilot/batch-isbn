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
        if not soup: return metadata_dict
        # Get metadata other than book title
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
        # Get title
        metadata_dict["书名"] = soup.find("a", class_="nbg")["title"]
        
    return metadata_dict

def retrieve_book_title(local_html):
    global webdriver
    with open(local_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")
        return soup.find("a", class_="nbg")["title"]

def get_source(url):
    global driver, sleep_interval, trial_times
    response = None
    for _ in range(trial_times):
        driver.get(url)
        state = driver.execute_script("return document.readyState")
        if state == "complete":
            response = BeautifulSoup(driver.page_source, "lxml")
            break
        time.sleep(sleep_interval)
    return response

def query_douban(book_info):
    base_url = "https://search.douban.com/book/subject_search?search_text="
    soup = get_source(base_url + book_info)
    return soup.find("a", class_="title-text")["href"] if soup else None

def add_metadata(metadata_dict):
    global metadata_sum
    for key in metadata_sum.keys():
        if key != "URL": metadata_sum[key].append(metadata_dict.get(key, "N/A"))

# Step 0: Initialize
driver = webdriver.Edge()
ckpt_file = "temp.pkl"
sleep_interval = 1
trial_times = 3
sheet = pd.read_excel("香港史课程推荐购买书目.xlsx")
book_list = sheet["书籍信息"].tolist()
metadata_sum = {"书名": [], "作者": [], "出版社": [], "出版年": [], "ISBN": [], "URL": []}
pbar = tqdm(total=len(book_list))

# Step 1: Query and get best match work
pbar.set_description(f"Fetching book URL (step 1/2)")
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
pbar.set_description(f"Fetching ISBN (step 2/2)")
for url in metadata_sum["URL"]:
    add_metadata(retrieve_metadata(url))
    pbar.update(1)
pbar.close()
driver.close()

# Step 3: Save to Excel, delete temp
for key in metadata_sum.keys():
    sheet[key] = metadata_sum[key]
sheet.to_excel("香港史课程推荐购买书目_Retrieved_V3.xlsx", index=False)
os.remove(ckpt_file)