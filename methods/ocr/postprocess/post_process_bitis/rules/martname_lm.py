import pdb
import unidecode
import Levenshtein
from .base_lm import Base_LM

class MartName_LM(Base_LM):
    def __init__(self, dict_path):
        super(MartName_LM, self).__init__()
        self.map_mart_name = {}
        self.map_store_id = {}
        self.map_address = {}
        self.values = []
        with open(dict_path, 'r', encoding='utf-8') as f:
            for row in f:
                store_id, mart_name, _, address = row[:-1].split('\t')
                self.map_mart_name[mart_name.lower()] = mart_name
                self.map_store_id[mart_name.lower()] = store_id
                self.map_address[mart_name.lower()] = address


    def find_best_match(self, text, dictionary, threshold):
        final_value = ''
        final_dict_value = ''
        max_score = 0.
        text_lower = unidecode.unidecode(text.lower())
        for value in dictionary.keys():
            score = 1.0 - (Levenshtein.distance(text_lower, unidecode.unidecode(dictionary[value]))/max(len(text_lower), len(value)))
            if score > max_score:
                final_value = self.map_mart_name[value]
                final_dict_value = dictionary[value]
                max_score = score
        pdb.set_trace()
        if max_score > threshold:
            return True, final_value
        else:
            return False, text


    def predict(self, address, mart_name):
        has_match, new_mart_name = self.find_best_match(mart_name, self.map_mart_name, 0.6)
        if not has_match:
            has_match, new_mart_name = self.find_best_match(address, self.map_mart_name, 0.5)
        if not has_match:
            has_match, new_mart_name = self.find_best_match(address, self.map_address, 0.4)
        if has_match:
            return new_mart_name, self.map_store_id[new_mart_name.lower()]
        return mart_name, ''