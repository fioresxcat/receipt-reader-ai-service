import re
import pdb
import numpy as np
from .base_lm import Base_LM

class Receipt_id_LM(Base_LM):
    def __init__(self, max_word):
        super(Receipt_id_LM, self).__init__()

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
        s = re.search('s(.*)n', res.lower())
        if s is not None:
            raw_res = s.group(1).upper()
            raw_res = re.sub('[^\d|A-Z]', '', raw_res)
            s1 = re.search('[A-Z]\d{2}[A-Z]{2}\d{6}', raw_res)
            if s1 is not None:
                res = s1.group(0)
            else:
                s2 = re.search('\d{2}[A-Z]{2}\d{6}', raw_res)
                if s2 is not None:
                    res = 'A' + s2.group(0)
                else:
                    res = raw_res
        return key, index, sub_key, res