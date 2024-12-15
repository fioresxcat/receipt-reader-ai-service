import numpy as np
from .base_lm import Base_LM
import re


class Receipt_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Receipt_id_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
        raw_res = ''.join(raw_words)
        s = re.search('\d+', raw_res)
        if s != None:
            res = s.group(0)
            return res
        return raw_res


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=2, max_word=self.max_words, max_char=15, charset='0123456789:T/N')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result