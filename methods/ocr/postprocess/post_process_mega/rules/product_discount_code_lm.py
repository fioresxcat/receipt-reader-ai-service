import re 
import pdb
from .base_lm import Base_LM


class ProductDiscountCode_LM(Base_LM):
    def __init__(self, max_words):
        super(ProductDiscountCode_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        words = []
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
            for word, prob in word_cand:
                s = re.search('^.*\d{8}$', word)
                if s != None:
                    new_word = s.group(0)
                    words.append(new_word)
                    break
        if len(words) == 0:
            words = raw_words
        return 'DC' + words[0][-8:]

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2, max_word=self.max_words, max_char=12)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result