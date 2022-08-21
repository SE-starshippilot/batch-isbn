import os
import pickle
from functools import wraps

from utils import updateBuffer, getb64encode

getCkptPath = lambda x: os.path.join(os.getcwd(), '.tmp', f'{getb64encode(x)}.pkl')

def maintainCheckpoint(io_func):
    @wraps(io_func)
    def io_func_wrapper(attr_dict:dict):
        ckpt_file_path = getCkptPath(attr_dict["input_path"])
        mode = 'rb' if io_func.__name__ == 'readCheckpoint' else 'wb'
        try:
            with open(ckpt_file_path, mode) as cf:
                io_func(cf, attr_dict)
        except:
            attr_dict.update({'save_path':attr_dict['input_path']})
            with open(ckpt_file_path, 'wb') as cf:
                pickle.dump(attr_dict, cf)

    return io_func_wrapper

@maintainCheckpoint
def readCheckpoint(file_writer:str, attr_dict:dict)->dict:
    attr_dict.update(pickle.load(file_writer))

@maintainCheckpoint
def writeCheckpoint(file_writer:str, attr_dict:dict)->None:
    pickle.dump(attr_dict, file_writer)