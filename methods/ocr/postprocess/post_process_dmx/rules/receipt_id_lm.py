import re
import pdb

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
                s = re.search('(\d{5})(SO|50)(\d{11})', word)
                if s != None:
                    new_word = s.group(1) + s.group(2).replace('50', 'SO') + s.group(3)
                    words.append(new_word)
                    break
        if len(words) == 0:
            words = raw_words
        if self.max_words == None:
            return ''.join(words)
        else:
            return ''.join(words[:self.max_words])


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=20, max_word=4, max_char=24)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result
