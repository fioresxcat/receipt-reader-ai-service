import re
import pdb

from .base_lm import Base_LM

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
        words = []
        raw_words = []
        for word_cand in word_cands:
            for word, prob in word_cand:
                if re.search('\d{6,15}', word) != None:
                    raw_words.append(word)
                    break
            for word, prob in word_cand:
                if re.search('^000000\d{8}$', word) != None:
                    words.append(word)
                    break
                if re.search('^0\d{13}$', word) != None and self.check_EAN(word[1:]):
                    words.append(word)
                    break
                if re.search('^\d{13}$', word) != None and self.check_EAN(word):
                    words.append(word)
                    break
        if len(words) == 0:
            words = raw_words
        if self.max_words == None:
            return ' '.join(words[:1])
        else:
            return ' '.join(words[:1])

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=5, max_word=self.max_words, max_char=15)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result