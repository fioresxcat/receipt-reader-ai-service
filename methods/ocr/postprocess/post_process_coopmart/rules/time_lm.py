import re
import pdb
from .base_lm import Base_LM

class Time_LM(Base_LM):
    def __init__(self, max_words):
        super(Time_LM, self).__init__()
        self.max_words = max_words


    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0 and len(word_cand[0]) != 0:
                raw_words.append(word_cand[0][0])
        word = ''.join(raw_words)
        s = re.search('(\d{1,2}):(\d{1,2}):(\d{1,2})', word)
        if s != None:
            res = s.group(0)
            return res
        return word


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=2, max_word=self.max_words, max_char=11, charset='0123456789:')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result