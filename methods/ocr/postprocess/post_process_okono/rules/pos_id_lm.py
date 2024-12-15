import re 
import pdb
import numpy as np
from .base_lm import Base_LM
import unidecode

class Pos_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Pos_id_LM, self).__init__()
        self.max_words = max_words

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
        result = unidecode.unidecode(' '.join(result))
        result = result.split('so')[-1].strip()
        return key, index, sub_key, result

