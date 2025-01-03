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
        s1 = re.search('\d{1,3}[\,\d{3}]*\,\d{2}', raw_res)
        s2 = re.search('\d{1,3}[\.\d{3}]*', '.'.join(raw_words).replace(',', '.'))
        if (s1 != None and s2 == None) or (s1 != None and s2 != None and len(s1.group(0)) >= len(s2.group(0))):
            res = s1.group(0)
            res = res[:-3] + '.' + res[-2:]
            return res
        if (s2 != None and s1 == None) or (s1 != None and s2 != None and len(s2.group(0)) > len(s1.group(0))):
            res = s2.group(0)
            # res = res.replace('.', ',') + '.00'
            res = res.replace(',', '.')
            return res
        return raw_res.replace(',', '.')
            
    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=1, max_word=self.max_words, max_char=16)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result
