import re
import pdb

from .base_lm import Base_LM

class Time_LM(Base_LM):
    def __init__(self, max_words):
        super(Time_LM, self).__init__()
        self.max_words = max_words
        self.hour_mapper = {
            'am': 0,
            'pm': 12,
        }

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
        raw_res = ''.join(raw_words)
        res = raw_res.lower().strip()
        s = re.search('(\d{1,2}):(\d{2}):(\d{2})(am|pm)$', res.replace(' ', ''))
        if s != None:
            hh = s.group(1)
            mm = s.group(2)
            ss = s.group(3)
            period = s.group(4)
            if int(hh) > 24:
                return raw_res
            if int(mm) > 59:
                return raw_res
            if int(ss) > 59:
                return raw_res
            if int(hh)+self.hour_mapper[period] < 24:
                hh = str(int(hh)+self.hour_mapper[period])
            if len(hh) == 1:
                hh = '0' + hh
            res = hh + ':' + mm + ':' + ss
            return res
        return raw_res
            
    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=1, max_word=self.max_words, max_char=16, charset='0123456789AMPM: ')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result