import pdb
import numpy as np
from .base_lm import Base_LM
import re


class Staff_LM(Base_LM):
    def __init__(self):
        super(Staff_LM, self).__init__()

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
        result = re.sub('[,;.-]', ':', ' '.join(result)).split(':')[-1]
        result = result.split('CashierName')[-1].strip()
        return key, index, sub_key, result