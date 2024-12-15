import re
from .base_lm import Base_LM


class Date_LM(Base_LM):
    def __init__(self, max_words):
        super(Date_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        words = []
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
            for word, prob in word_cand:
                s = re.search('(\d{1,2})\.(\d{1,2})\.(\d{4})', word)
                if s != None:
                    dd = s.group(1)
                    mm = s.group(2)
                    yy = s.group(3)
                    if int(dd) > 31 or int(dd) < 1:
                        continue
                    if int(mm) > 12 or int(mm) < 1:
                        continue
                    if int(yy) < 2000 or int(yy) > 2050:
                        continue
                    if len(dd) == 1:
                        dd = '0' + dd
                    if len(mm) == 1:
                        mm = '0' + mm
                    words.append(dd + '/' + mm + '/' + yy)
                    break
        if len(words) == 0:
            words = raw_words
        if self.max_words == None:
            return ' '.join(words)
        else:
            return ' '.join(words[:self.max_words])

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=11)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result