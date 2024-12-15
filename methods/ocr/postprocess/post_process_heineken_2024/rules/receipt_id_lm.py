import re
import pdb
import numpy as np
from .base_lm import Base_LM

class Receipt_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Receipt_id_LM, self).__init__()
        self.max_words = max_words

    def predict(self, key, index, sub_key, char_cands, charset_list):
        result = []
        for w_cand in char_cands[:self.max_words]:
            word = ''
            for char_cand in w_cand:
                char = charset_list[np.argmax(char_cand)]
                if char == '<nul>':
                    break
                word += char
            result.append(word)
        result = ' '.join(result)
        result = re.split('\:|\s', result.strip())[-1]
        result = result.replace('T', '1')
        result = result.replace('O', '0')
        result = result.replace('o', '0')
        return key, index, sub_key, result