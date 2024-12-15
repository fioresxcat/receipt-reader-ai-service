import re 
import pdb
from .base_lm import Base_LM


class Money_LM(Base_LM):
    def __init__(self, max_words):
        super(Money_LM, self).__init__()
        self.max_words = max_words

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            raw_words.append(word_cand[0][0])
        raw_res = ','.join(raw_words).replace('.', ',')
        while ',,' in raw_res:
            raw_res = raw_res.replace(',,', ',')
        s = re.search('^\d{1,3}[\,\d{3}]*', raw_res)
        if s != None:
            res = s.group(0)
            if re.search('\,\d{2}$', res) != None:
                temp = re.search('\,\d{2}$', res).group(0) + '0'
                res = re.sub('\,\d{2}$', temp, res)
            return res
        return raw_res.replace('.', ',')
            
    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=1, max_word=self.max_words, max_char=16)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result
