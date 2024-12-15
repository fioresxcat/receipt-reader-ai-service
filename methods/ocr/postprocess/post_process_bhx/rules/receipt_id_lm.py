import re
import pdb
from .base_lm import Base_LM

class Reciept_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Reciept_id_LM, self).__init__()
        self.max_words = max_words

    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=2, max_word=self.max_words, max_char=17, charset='0123456789')
        result = ''
        if len(word_cands[0]) != 0:
            result = word_cands[0][0][0][:17]
        return key, index, sub_key, result