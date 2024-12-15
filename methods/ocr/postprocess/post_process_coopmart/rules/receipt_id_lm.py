import re
from .base_lm import Base_LM

class Receipt_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Receipt_id_LM, self).__init__()
        self.max_words = max_words


    def check_rule(self, word_cands):
        words = []
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
            for word, prob in word_cand:
                s = re.search('(^\d{5}$)', word.split(':')[-1].strip())
                if s != None:
                    words.append(s.group(1))
                    break
            if len(words) > 0:
                break

        if len(words) == 0:
            words = raw_words
        if self.max_words == None:
            return ''.join(words)
        else:
            return ''.join(words[:self.max_words])


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=12)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result