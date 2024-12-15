import re
import pdb

from .base_lm import Base_LM

class Date_LM(Base_LM):
    def __init__(self, max_words):
        super(Date_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
        raw_res = '/'.join(raw_words)
        while '//' in raw_res:
            raw_res = raw_res.replace('//', '/')
        s = re.search('^(\d{1,2})\/(\d{1,2})\/(\d{4})$', raw_res)
        if s != None:
            mm = s.group(1)
            dd = s.group(2)
            yy = s.group(3)
            if int(dd) > 31 or int(dd) < 1:
                return raw_res
            if int(mm) > 12 or int(mm) < 1:
                return raw_res
            if int(yy) < 2000 or int(yy) > 2050:
                return raw_res
            if len(dd) == 1:
                dd = '0' + dd
            if len(mm) == 1:
                mm = '0' + mm
            res = dd + '/' + mm + '/' + yy
            return res
        return raw_res
            
    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=1, max_word=self.max_words, max_char=16, charset='0123456789/')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result