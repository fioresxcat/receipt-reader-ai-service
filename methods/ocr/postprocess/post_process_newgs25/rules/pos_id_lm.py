import re 
import pdb
import numpy as np
from .base_lm import Base_LM

class Pos_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Pos_id_LM, self).__init__()
        self.max_words = max_words

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=1, max_word=self.max_words, max_char=16, charset='0123456789VN- ')
        result = ''
        if len(word_cands[0]) != 0:
            result = word_cands[0][0][0].split('-')[0]
            s = re.search('VN\d{6}', result)
            if s is not None:
                result = s.group(0)
        return key, index, sub_key, result

