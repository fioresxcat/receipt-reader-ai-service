import os
import re
import unidecode
import Levenshtein
import numpy as np


class DateFormater:
    def __init__(self):
        pass

    def predict(self, raw_text):
        text = unidecode.unidecode(raw_text.lower())
        raw_result = []
        s = re.search('(\d{1,2})\s+thang\s+(\d{1,2})\s+nam\s+(\d{4})', text)
        if s is not None:
            raw_result = [s.group(1), s.group(2), s.group(3)]
        else:
            temp_result = '/'.join(re.split('[^\d]+', text))
            s = re.search('\d{1,2}\/\d{1,2}\/\d{4}', temp_result)
            if s is not None:
                raw_result = s.group(0).split('/')
        if len(raw_result) == 0:
            return raw_text
        for i in range(len(raw_result)):
            if len(raw_result[i]) == 1:
                raw_result[i] = '0' + raw_result[i]
        result = '/'.join(raw_result)
        return result



class Formater:
    def __init__(self, mapper):
        self.formaters = {
            'date_formater': DateFormater()
        }
        self.mapper = mapper

    def predict(self, res):
        for key in res:
            if type(res[key]) == list:
                new_value = []
                if key in self.mapper.keys():
                    for sub_value in res[key]:
                        new_value.append(self.formaters[self.mapper[key]].predict(sub_value))
                else:
                    new_value = res[key]
            elif type(res[key]) == str:
                if key in self.mapper.keys():
                    new_value = self.formaters[self.mapper[key]].predict(res[key])
                else:
                    new_value = res[key]
            res[key] = new_value
        return res
        