import re
import pdb
import unidecode

from .base_lm import Base_LM

class Martname_LM(Base_LM):
    def __init__(self, dict_path, max_words):
        super(Martname_LM, self).__init__()
        self.map = {}
        self.values = []
        self.max_words = max_words
        with open(dict_path, 'r', encoding='utf-8') as f:
            for row in f:
                mart_id, mart_name = row[:-1].split('\t')
                self.map[mart_id] = mart_name


    def check_rule(self, pos_id):
        s = re.search('VN\d{4}', pos_id)
        mart_name = ''
        mart_id = ''
        if s is not None:
            mart_id = s.group(0)
        if mart_id in self.map.keys():
            mart_name = self.map[mart_id]
        return mart_name


    def predict(self, key, index, sub_key, pos_id, charset_list):
        result = self.check_rule(pos_id)
        return key, index, sub_key, result