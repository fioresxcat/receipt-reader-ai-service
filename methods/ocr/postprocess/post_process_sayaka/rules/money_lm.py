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
            raw_words.append(word_cand[0][0])
        raw_res = ''.join(raw_words).replace('.', ',')
        raw_res = re.sub('\,+', ',', raw_res)
        s = re.search('\-?\d{1,3}([\,|\s]\d{3})*', raw_res)
        if s != None:
            res = s.group(0).replace(' ', ',')
            return res
        return raw_res

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=1, max_word=self.max_words, max_char=20, max_char_cand=10, charset='0123456789dđ/ .,:-')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result