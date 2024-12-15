import re
from .base_lm import Base_LM
import pdb


class Product_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Product_id_LM, self).__init__()
        self.max_words = max_words

    def check_EAN(self, string):
        odd = 0
        even = 0
        for i in range(len(string)-1):
            if (i+1) % 2 == 0:
                even += int(string[i])
            else:
                odd += int(string[i])
        if (odd + 3*even + int(string[-1])) % 10 == 0:
            return True
        return False

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
        raw_res = ''.join(raw_words)
        

        # s = re.search('^000000\d{8}$', raw_res)
        # if s != None:
        #     res = s.group(0)
        # s = re.search('^\d{15}$', raw_res)
        # if s != None:
        #     res = s.group(0)
        # s = re.search('^\d{13}$', raw_res)
        # if s != None:
        #     res = s.group(0)
        # print (raw_res, len (raw_res), res)
        # if res != None:
        #     return res
        
        
        return raw_res

    def predict(self, key, index, sub_key, char_cands, charset_list):
        # word_cands = self.get_word_cands(char_cands, charset_list, k=1, max_word=self.max_words, max_char=20)
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=2, max_word=self.max_words, max_char=15, charset='0123456789')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result