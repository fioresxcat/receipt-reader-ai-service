import re
import pdb

from datetime import datetime
from .base_lm import Base_LM

class Time_LM(Base_LM):
    def __init__(self, max_words):
        super(Time_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        time_s = None
        time_e = None
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
            for word, prob in word_cand:
                s = re.search('(\d{1,2}):(\d{1,2})', word)
                if s != None:
                    hh = s.group(1)
                    mm = s.group(2)
                    if int(hh) > 24:
                        continue
                    if int(mm) > 60:
                        continue
                    time_s = hh + ':' + mm
                    break
            for word, prob in word_cand:
                for char in word:
                    if char.lower() == 'a':
                        time_e = 'am'
                    if char.lower() == 'p':
                        time_e = 'pm'
                    if time_e is not None:
                        break
                if time_e is not None:
                        break

        if time_s != None:
            if time_e != None:
                in_time = datetime.strptime(time_s + ' ' + time_e, "%I:%M %p")
                out_time = datetime.strftime(in_time, "%H:%M")
                return out_time
            else:
                return time_s
        return ' '.join(raw_words[:self.max_words])


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=8)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result