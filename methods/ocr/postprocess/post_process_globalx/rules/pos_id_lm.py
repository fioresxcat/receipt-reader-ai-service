import re
import pdb
import numpy as np
from .base_lm import Base_LM

class Pos_id_LM(Base_LM):
    def __init__(self):
        super(Pos_id_LM, self).__init__()

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
        result = raw_result = ' '.join(raw_result)
        s = re.search('\d+$', raw_result)
        if s is not None:
            result = s.group(0)[-6:]
        return key, index, sub_key, result