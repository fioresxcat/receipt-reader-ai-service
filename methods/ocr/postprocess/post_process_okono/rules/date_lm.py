import re
import pdb
import numpy as np
from .base_lm import Base_LM

class Date_LM(Base_LM):
    def __init__(self, max_word):
        super(Date_LM, self).__init__()

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
        res = ' '.join(result)
        s = re.search('n(.*)$', res.lower())
        if s is not None:
            raw_res = s.group(1)
            raw_res = re.sub('[^\d]', '', raw_res)
            dd = ''
            mm = ''
            yy = ''
            if len(raw_res) >= 2:
                dd = raw_res[:2]
            if len(raw_res) >= 4:
                mm = raw_res[2:4]
            if len(raw_res) >= 4:
                yy = raw_res[4:]
            res = dd + '/' + mm + '/' + yy
        return key, index, sub_key, res