import re
import pdb
from .base_lm import Base_LM

class Time_LM(Base_LM):
    def __init__(self, max_words):
        super(Time_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        cand_raw_probs = self.get_sentence_cands(word_cands, 20)
        words = []
        raw_words = cand_raw_probs[0][1]
        for _, word_cand, _ in cand_raw_probs:
            word = ':'.join(word_cand)
            word = word.replace('T', '1')
            word = word.replace('O', '0')
            s = re.search('(\d{1,2}):(\d{1,2}):(\d{1,2})', word)
            if s != None:
                hh = s.group(1)
                mm = s.group(2)
                ss = s.group(3)
                if int(hh) > 24:
                    continue
                if int(mm) > 60:
                    continue
                if int(ss) > 60:
                    continue
                words.append(s.group(0))
                break
        if len(words) == 0:
            words = raw_words
        if self.max_words == None:
            return ':'.join(words)
        else:
            return ':'.join(words[:self.max_words])

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=5, max_word=self.max_words, max_char=11)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result