import re 
import pdb
from .base_lm import Base_LM

class Discount_Money_LM(Base_LM):
    def __init__(self, max_words):
        super(Discount_Money_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        words = []
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
            for word, prob in word_cand:
                s = re.search('^\-\d{1,3}[\.\d{3}]*$', word.replace(',', '.'))
                if s != None:
                    new_word = s.group(0)
                    words.append(new_word)
                    break
        if len(words) == 0:
            return raw_words[0]
        res = 0
        for word in words:
            res += int(word.replace('.', ''))
        res = str(res)
        sum_discount = ''
        for i in range(len(res)):
            sum_discount = res[len(res)-1-i] + sum_discount
            if i % 3 == 2 and i != len(res) - 1:
                sum_discount = '.' + sum_discount
        sum_discount = sum_discount.replace('-.', '-')
        return sum_discount
            

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=16)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result
