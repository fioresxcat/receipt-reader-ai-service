import re 
import pdb
from .base_lm import Base_LM


class VAT_LM(Base_LM):
    def __init__(self, max_words):
        super(VAT_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
        raw_res = ''.join(raw_words).replace(' ', '')
        s = re.search('\d+\%', raw_res)
        if s != None:
            res = 'VAT' + s.group(0)
            return res
        return raw_res

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=8)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result
