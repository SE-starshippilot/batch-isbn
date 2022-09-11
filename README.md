# Batch ISBN Fetcher
This repository contains the source code and releases of Batch ISBN Fetcher, an application that retrieves ISBN given a book title, author, publisher and date.

## How to use

1. Clone repository

```shell
git clone https://github.com/SE-starshippilot/batch-isbn.git
```

2. Install pip dependencies

```shell
pip install -r requirements.txt
```

3. Prepare the books you wish to retrieve using the [template](./template/sample.xlsx)

4. Run the `gui.py`

```
python gui.py
```

## The GUI

I designed the GUI as intuitive and simple (at least I hope so)

​	👉`Browse` the excel file you wish to process.

​	👉`Start` or `Pause` the process.

​	👉 (Optional) `preview` the file you selected.

​	👉 (Optional) `reset progress` if you wish to start over (in case you append new entries, etc.).**Please notice, this will not erase retrieved information!**

​	👉(Optional) `save as` if you want to save to another file. **By default, the program saves changes to the original file.**

​	👉(Optional) `add retrieved info` if you want the program to append found information to excel. By default not ticked. **This will generate additional columns in the excel if you ticked, and remove them when unticked.**

​	👉(Optional) `output verbosity` can be changed. By default it's INFO. But you can change to one of `DEBUG`, `INFO`, `WARN`, `ERROR`. The output box in the right will show less information if you set the verbosity higher.

When the process finishes, it will pop up a window to inform the user.

**Changes will only take into affect when you exit the program.**



## Known bugs

- This script <u>DOES NOT GUARANTEE</u> correctness. It is possible it retrieves wrong info or raise error even it finds correct info
- I haven't have time to implement multithreading (async) to process multiple books in the same time, so performance is expected to suck. SORRY!
- Will fall into manual searching if any of the field is left blank

## Future work

Currently I don't have effort or time to implement the following features. I will do so in the far, far future.....

- [ ] Implement async and multithread queries.
- [ ] More flexible carrier.
- [ ] Counter Amazon and Douban's anti-scrapping technique.

## Contribution, Suggestions and Bugs

Currently I do not accept any pull requests, but feel free to create issues if you encounter bugs.

Or, if you have time, you can fork this repo.