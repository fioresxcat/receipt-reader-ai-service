import re
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
        result = ''.join(result)
        raw_result = result.split(':')[-1].replace('O', '0')
        s = re.search('\d{15}', raw_result)
        if s != None:
            result = s.group(0)
        else:
            result = raw_result
        return key, index, sub_key, result