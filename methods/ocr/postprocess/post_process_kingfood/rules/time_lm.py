import re
import pdb
import numpy as np
from .base_lm import Base_LM

class Time_LM(Base_LM):
    def __init__(self):
        super(Time_LM, self).__init__()

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
        # find time has true form
        s = re.search('\d{1,2}[\:|\.]\d{2}$', raw_result)
        if s is not None:
            result = s.group(0).replace('.', ':')
        # find date has no :
        else:
            s = re.search('[\s|\.]\d{4}$', raw_result)
            if s is not None:
                cand = s.group(0)
                result = cand[:2] + ':' + cand[2:4]
        return key, index, sub_key, result