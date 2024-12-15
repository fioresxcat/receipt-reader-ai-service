import re
import pdb
import numpy as np

from datetime import datetime
from .base_lm import Base_LM

class Time_LM(Base_LM):
    def __init__(self, max_word):
        super(Time_LM, self).__init__()

    def predict(self, key, index, sub_key, char_cands, charset_list):
        result = []
        for w_cand in char_cands:
            word = ''
            for char_cand in w_cand:
                char = charset_list[np.argmax(char_cand)]
                if char == '<nul>':
                    break
                word += char
            result.append(word)
        res = ''.join(result)
        # get time only
        raw_time = re.sub('[^\d]', '', res)
        time = None
        if len(raw_time) >= 2:
            time = raw_time[-2:]
        if len(raw_time) >= 4:
            time = raw_time[-4:-2] + ':' + time
        if len(raw_time) >= 5:
            time = raw_time[-6:-4] + ':' + time
        # get end
        end = 'am'
        if 'p' in res.lower():
            end = 'pm'
        if time is not None:
            try:
                in_time = datetime.strptime(time + ' ' + end, "%I:%M:%S %p")
                res = datetime.strftime(in_time, "%H:%M:%S")
            except:
                res = re.sub('[^\d|\:]', '', res)
        return key, index, sub_key, res