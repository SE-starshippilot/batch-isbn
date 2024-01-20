import os
import json
import pickle
import logging
import traceback
import pandas as pd
from tqdm import tqdm
from typing import Any
from easydict import EasyDict
from collections import namedtuple

from isbn_retriever import ISBNRetriever


def is_valid_isbn(isbn:Any)->bool:
    if not(isinstance(isbn, str)): return False
    if isbn == 'N/A': return True # We already searched and cannot find the book
    isbn = isbn.replace('-', '').replace(' ', '')  # Remove hyphens and spaces

    if len(isbn) == 10:
        total = sum(int(num) * weight for num, weight in zip(isbn[:9], range(1, 10)))
        check = 11 - (total % 11)
        if check == 11:
            check = '0'
        elif check == 10:
            check = 'X'
        else:
            check = str(check)
        return isbn[-1] == check
    elif len(isbn) == 13:
        total = sum(int(num) * (1 if idx % 2 == 0 else 3) for idx, num in enumerate(isbn[:12]))
        check = 10 - (total % 10)
        if check == 10:
            check = '0'
        else:
            check = str(check)
        return isbn[-1] == check
    else:
        return False

# Step 0: Initialize
ckpt_file_name = "temp.pkl"
source_file_name = '/Users/shitianhao/Documents/GitHub/batch-isbn/testing.xlsx'
add_fetched_attribute = True
start_from_scratch = True
retrieve_attributes = ['Fetched Title', 'Fetched Authors', 'Fetched Publisher', 'Fetched Edition Date', 'Search URL', 'ISBN']
retriever = ISBNRetriever()

sheet = pd.read_excel(source_file_name, keep_default_na=False) # Change to handle different files

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("log.txt", mode='w')
formatter = logging.Formatter('[%(levelname)s]:%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

def main():
    # load checkpoint
    if os.path.exists(ckpt_file_name) and not(start_from_scratch):
        with open(ckpt_file_name, "rb") as f:
            processing_status = pickle.load(f)
    else:
        processing_status = EasyDict({'start_index':0, 'skipped_records':0})
    pbar = tqdm(total=len(sheet) - processing_status.start_index, desc="Fetching metadata", unit="record(s)")

    if add_fetched_attribute:
        # add new columns if missing
        for retrieve_attribute in retrieve_attributes:
            if retrieve_attribute not in sheet.columns:
                sheet[retrieve_attribute] = None
    try:
        for index, row in sheet[processing_status.start_index:].iterrows():
            pbar.update(1)
            logger.info('*'*20)
            if is_valid_isbn(row['ISBN']): 
                logger.info(f'ISBN {row["ISBN"]} is valid, skipping...')
                processing_status.skipped_records += 1
                continue

            logger.info("Searched")
            for attr, value in row.items():
                if value:
                    logger.info(f"\t{attr}: {value}")

            retrieved_info = retriever(row)
            
            logger.info("Received")
            for attr in retrieve_attributes:
                value = retrieved_info.get(attr, 'N/A')
                logger.info(f"\t{attr}: {value}")
                sheet.loc[index, attr] = value
    except Exception as e:
        print("Interrupted.")
        traceback.print_exc()
    else:
        print("Finished.")
    finally:
        retriever.quit()
        print("Saving checkpoint...")
        processing_status.start_index = index
        with open(ckpt_file_name, "wb") as f:
            pickle.dump(processing_status, f)
        print("Checkpoint saved.")

        sheet.to_excel(source_file_name, index=False)
        pbar.close()
    
if __name__ == '__main__':
    main()
    # logger.info("Searching:")
    # for attr in ['Title', 'Author', 'Publisher', 'Edition Date']:
    #     logger.info(f"\t{attr}: {row[attr]}")
# save to excel




# pbar.set_description(f"Fetching book URL (step 1/2)")
# book_query_url = []
# if os.path.exists(ckpt_file):
#     with open(ckpt_file, "rb") as f:
#         metadata_sum = pickle.load(f)
#     pbar.update(len(metadata_sum["URL"]))
# else:
#     for book_info in book_list:
#         pbar.update(1)
#         url = query_douban(book_info)   # extend to use different providers
#         metadata_sum["URL"].append(url)
#     with open(ckpt_file, "wb") as f:
#         pickle.dump(metadata_sum, f)
# pbar.reset()

# # Step 2: Retrieve metadata
# pbar.set_description(f"Fetching ISBN (step 2/2)")
# for url in metadata_sum["URL"]:
#     add_metadata(retrieve_metadata(url))
#     pbar.update(1)

# # Step 3: Save to Excel, delete temp
# for key in metadata_sum.keys():
#     sheet[key] = metadata_sum[key]
# sheet.to_excel("Retrieved.xlsx", index=False)
# os.remove(ckpt_file)