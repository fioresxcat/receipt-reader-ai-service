import re
import pdb
import numpy as np
from .base_lm import Base_LM

class Date_LM(Base_LM):
    def __init__(self):
        super(Date_LM, self).__init__()

    def predict(self, key, index, sub_key, char_cands, charset_list):
        raw_result = []
        for w_cand in char_cands:
            word = ''
            for char_cand in w_cand:
                char = charset_list[np.argmax(char_cand)]
                if char == '<nul>':
                    break
                word += char
            raw_result.append(word)
        result = raw_result = ''.join(raw_result).replace(' ', '')
        # find date has true form
        s = re.search('(\d{1,2})[\/|\-](\d{1,2})[\/|\-](\d{4})', raw_result)
        if s is not None:
            dd = s.group(1)
            mm = s.group(2)
            yy = s.group(3)
            result = dd + '/' + mm + '/' + yy
        return key, index, sub_key, result