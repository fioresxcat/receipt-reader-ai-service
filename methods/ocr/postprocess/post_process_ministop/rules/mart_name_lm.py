import pdb
import math
import unidecode
from .base_lm import Base_LM

class Martname_LM(Base_LM):
    def __init__(self, dict_path, max_words):
        super(Martname_LM, self).__init__()
        self.map = {}
        self.values = set()
        self.max_words = max_words
        self.threshold = 0.1
        with open(dict_path, 'r', encoding='utf-8') as f:
            for row in f:
                raw = row[:-1]
                self.values.add(unidecode.unidecode(raw.lower()))
                self.map[unidecode.unidecode(raw.lower())] = raw


    def check_rule(self, word_cands):
        list_str = []
        for word_cand in word_cands:
            list_str.append(word_cand[0][0])
        final_value = ''
        min_score = 10000
        if self.max_words == None:
            string = unidecode.unidecode(' '.join(list_str).lower())
            for value in self.values:
                score = self.edit_distance(string, unidecode.unidecode(value.lower()))
                if score < min_score:
                    final_value = self.map[value]
                    min_score = score
            if min_score > math.ceil(len(string)*self.threshold):
                final_value = ' '.join(list_str)
        elif self.max_words == 1:
            for string in list_str:
                for value in self.values:
                    score = self.edit_distance(string.lower(), value.lower())
                    if score < min_score:
                        final_value = self.map[value]
                        min_score = score
        
        return final_value


    def edit_distance(self, s1, s2):#levenshtein
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]


    def predict(self, key, index, sub_key, char_cands, charset_list):
        word_cands = self.get_word_cands(char_cands, charset_list, k=2)
        result = self.check_rule(word_cands)
        return key, index, sub_key, result