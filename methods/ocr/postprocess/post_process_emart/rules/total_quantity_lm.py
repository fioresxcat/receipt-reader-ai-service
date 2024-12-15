import re
from .base_lm import Base_LM

class Total_Quantity_LM(Base_LM):
    def __init__(self, max_word):
        super(Total_Quantity_LM, self).__init__()
        self.max_words = max_word

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
            
        if self.max_words == None:
            return ''.join(raw_words).replace ('.','').replace (',','').replace ('-','')
        else:
            return ''.join(raw_words[:self.max_words]).replace ('.','').replace (',','').replace ('-','')


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=2, max_word=self.max_words, max_char=11, charset='0123456789.,-')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result