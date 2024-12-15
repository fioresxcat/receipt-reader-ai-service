import re 
import pdb
from .base_lm import Base_LM

class TaxCode_LM(Base_LM):
    def __init__(self, max_words):
        super(TaxCode_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        words = []
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
        raw_res = ' '.join(raw_words)
        s = re.search('\d{10}\-\d{3}$', raw_res)
        if s != None:
            return s.group(0)
        s = re.search('\d{10}$', raw_res)
        if s != None:
            return s.group(0)
        res = ''
        for c in raw_res:
            if c.isdigit() or c == '-':
                res += c
        return res

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=1, max_word=self.max_words, max_char=20)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result