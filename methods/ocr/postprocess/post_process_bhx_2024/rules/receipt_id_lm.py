import re
import pdb
import numpy as np
from .base_lm import Base_LM

class Receipt_id_LM(Base_LM):
    def __init__(self):
        super(Receipt_id_LM, self).__init__()

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
        raw_result = ' '.join(raw_result)
        list_cands = re.findall('\d+', raw_result)
        if len(list_cands) == 0:
            result = raw_result
        else:
            list_cands.sort(key = lambda x: -len(x))
            result = list_cands[0]
        return key, index, sub_key, result