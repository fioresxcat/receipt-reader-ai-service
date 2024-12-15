import re
import pdb

from .base_lm import Base_LM

class Date_LM(Base_LM):
    def __init__(self, max_words):
        super(Date_LM, self).__init__()
        self.max_words = max_words
        self.month_mapper = {
            '01': ['jan', 'ian', 'lan'],
            '02': ['feb'],
            '03': ['mar'],
            '04': ['apr'],
            '05': ['may'],
            '06': ['jun', 'iun', 'lun'],
            '07': ['jul', 'iul', 'lul', 'jui'],
            '08': ['aug'],
            '09': ['sep'],
            '10': ['oct', '0ct'],
            '11': ['nov'],
            '12': ['dec']
        }

    def check_rule(self, word_cands):
        raw_words = []
        for word_cand in word_cands:
            if len(word_cand) != 0:
                raw_words.append(word_cand[0][0])
        raw_res = '/'.join(raw_words).lower()
        raw_res = re.sub('[ ]+', '/', raw_res)
        while '//' in raw_res:
            raw_res = raw_res.replace('//', '/')
        for key in self.month_mapper.keys():
            for pattern in self.month_mapper[key]:
                raw_res = raw_res.replace(pattern, key)
        s = re.search('^(\d{1,2})\/(\d{1,2})\/(\d{4})$', raw_res)
        if s != None:
            dd = s.group(1)
            mm = s.group(2)
            yy = s.group(3)
            if int(dd) > 31 or int(dd) < 1:
                return raw_res
            if int(mm) > 12 or int(mm) < 1:
                return raw_res
            if int(yy) < 2000 or int(yy) > 2050:
                return raw_res
            if len(dd) == 1:
                dd = '0' + dd
            if len(mm) == 1:
                mm = '0' + mm
            res = dd + '/' + mm + '/' + yy
            return res
        return raw_res
            
    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands_num(char_cands, charset_list, k=1, max_word=self.max_words, max_char=16, charset='0123456789ADFJMNOSabceglnoprtuvy ')
        result = self.check_rule(word_cands)
        return key, index, sub_key, result