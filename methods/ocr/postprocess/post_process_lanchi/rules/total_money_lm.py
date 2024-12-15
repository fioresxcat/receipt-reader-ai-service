import re 
import pdb
from .base_lm import Base_LM


class Total_Money_LM(Base_LM):
    def __init__(self, max_words):
        super(Total_Money_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])

        list_res = []
        for raw_word in raw_words:
            raw_res = raw_word.replace(',', '.')
            while '..' in raw_res:
                raw_res = raw_res.replace('..', '.')
            s = re.search('^\-?\d{1,3}(\.\d{3})*d$', raw_res)
            if s != None:
                res = s.group(0)
                list_res.append(res)
                continue
            s = re.search('^\-?\d{1,3}(\.\d{3})*0$', raw_res)
            if s != None:
                res = s.group(0)[:-1] + 'd'
                list_res.append(res)
                continue
            list_res.append(raw_res)
        return list_res
            
    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=1, max_word=self.max_words, max_char=16)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result
