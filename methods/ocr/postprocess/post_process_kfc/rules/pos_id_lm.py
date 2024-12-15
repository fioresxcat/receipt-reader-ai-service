import re

from .base_lm import Base_LM

class Pos_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Pos_id_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
        res = ''.join(raw_words)
        s = re.search('\d{4}', res)
        if s != None:
            res = s.group()
        return res


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=13)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result