import numpy as np
from .base_lm import Base_LM


class Receipt_id_LM(Base_LM):
    def __init__(self, max_words):
        super(Receipt_id_LM, self).__init__()
        self.max_words = max_words

    def predict(self, key, index, sub_key, char_cands, charset_list):
        words = []
        for w_cand in char_cands:
            word = ''
            for char_cand in w_cand:
                char = charset_list[np.argmax(char_cand)]
                if char == '<nul>':
                    break
                word += char
            words.append(word)
        result = ' '.join(words)
        result = result.split(':')[-1]
        return key, index, sub_key, result