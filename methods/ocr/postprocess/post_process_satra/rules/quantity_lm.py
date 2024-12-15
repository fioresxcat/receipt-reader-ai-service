import re
from .base_lm import Base_LM
import pdb


class Quantity_LM(Base_LM):
    def __init__(self, max_word):
        super(Quantity_LM, self).__init__()
        self.max_words = max_word

    def check_rule(self, word_cands):
        words = []
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
            
            for word, prob in word_cand:
                s = re.search('^\d{1,3}(\.\d{2,3})$', word.replace(',', '.'))
                # pdb.set_trace()
                if s != None:
                    res = s.group(0)
                    last_characters = res.split ('.') [-1]
                    if last_characters == '00' or last_characters == '000':
                        res = ''.join (res.split ('.') [:-1])
                        return res

        if self.max_words == None:
            return ''.join(raw_words)
        else:
            return ''.join(raw_words[:self.max_words])


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=11)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result