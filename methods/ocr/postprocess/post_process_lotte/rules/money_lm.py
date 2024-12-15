import re 
import pdb
from .base_lm import Base_LM

class Money_LM(Base_LM):
    def __init__(self, max_words):
        super(Money_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
        raw_res = '.'.join(raw_words)
        raw_res = re.sub('[\,|\.]+', ',', raw_res)
        s = re.search('^\-?\d{1,3}(\,\d{3})*$', raw_res)
        if s != None:
            res = s.group(0)
            return res
        if re.search('^[\d]+$', raw_res) is not None:
            res = []
            while len(raw_res) != 0:
                res = [raw_res[-3:]] + res
                raw_res = raw_res[:-3]
            res = ','.join(res)
            return res
        s = re.search('^\-?\d{1,3}(\,\d{3})*', raw_res)
        if s != None:
            res = s.group(0)
            return res
        return raw_res

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=1, max_word=self.max_words, max_char=20)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result
