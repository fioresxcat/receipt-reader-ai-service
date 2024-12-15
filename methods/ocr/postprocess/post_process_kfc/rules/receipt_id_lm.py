import re

from .base_lm import Base_LM

class Receipt_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Receipt_id_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
        raw_res = ''.join(raw_words).replace (' ', '')
        res = re.sub('[\_:]', '-', raw_res)
        s = re.search('\d{3}\-\d{3}\-\d{7}', res)
        if s != None:
            res = s.group()
            return res.strip()
        return raw_res.strip()


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=2, max_word=self.max_words, max_char=20, charset='0123456789-\_:Invoice ')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result