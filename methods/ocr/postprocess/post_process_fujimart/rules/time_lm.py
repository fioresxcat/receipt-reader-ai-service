import re
import pdb
from .base_lm import Base_LM

class Time_LM(Base_LM):
    def __init__(self, max_words):
        super(Time_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        words = []
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
            for word, prob in word_cand:
                if len(word.split('-')) >= 2:
                    norm_word = re.sub('[^\d]', '', word.split('-')[1])
                    if len(norm_word) >= 4:
                        words.append(norm_word[:2] + ':' + norm_word[-2:])
                        break
                s = re.search('(\d{1,2}):(\d{1,2})', word)
                if s != None:
                    hh = s.group(1)
                    mm = s.group(2)
                    if int(hh) > 24:
                        continue
                    if int(mm) > 60:
                        continue
                    words.append(s.group(0))
                    break
        if len(words) == 0:
            words = raw_words
        if self.max_words == None:
            return ' '.join(words)
        else:
            return ' '.join(words[:self.max_words])


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=20)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result