import re
import pdb

from .base_lm import Base_LM

class Time_LM(Base_LM):
    def __init__(self, max_words):
        super(Time_LM, self).__init__()
        self.max_words = max_words
        self.hour_mapper = {
            'sa': 0,
            'ch': 12,
        }

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
        raw_res = ''.join(raw_words).lower().strip()
        s = re.search('(\d{1,2}):(\d{2})(sa|ch)$', raw_res)
        if s != None:
            hh = s.group(1)
            mm = s.group(2)
            period = s.group(3)
            if int(hh) > 11:
                return raw_res
            if int(mm) > 59:
                return raw_res
            hh = str(int(hh)+self.hour_mapper[period])
            if len(hh) == 1:
                hh = '0' + hh
            res = hh + ':' + mm
            return res
        return raw_res
            
    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=1, max_word=self.max_words, max_char=16, charset='0123456789SAtosaCHch: ')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result