import re
import pdb
import numpy as np
from .base_lm import Base_LM


class Receipt_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Receipt_id_LM, self).__init__()
        self.max_words = max_words

    def predict(self, key, index, sub_key, char_cands, charset_list):
        raw_result = ''
        for char_cand in char_cands[0]:
            char = charset_list[np.argmax(char_cand)]
            raw_result += char
        raw_result = raw_result.replace('<nul>', '')
       
        while len(raw_result) > 3 and not raw_result[-3:].isdigit():
            raw_result = raw_result[:-1]
        if len(raw_result) < 12:
            result = raw_result
        else:
            result = ''
            for i, raw_char_cand in enumerate(char_cands[0][len(raw_result)-12:len(raw_result)]):
                char_cand = zip(charset_list, raw_char_cand)
                char_cand = sorted(char_cand, key=lambda x: -x[1])
                for char, _ in char_cand:
                    if i in [5, 6]:
                        if char in 'AB':
                            result += char
                            break
                    else:
                        if char in '0123456789':
                            result += char
                            break
        return key, index, sub_key, result