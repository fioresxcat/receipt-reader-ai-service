import os
import pdb
import cv2
import numpy as np 

from modules.base_module import BaseModule
from .pp_config import pp_config
from .rules import *

class PostProcessorGS25(BaseModule):
    def __init__(self, common_config, model_config):
        super(PostProcessorGS25, self).__init__(common_config, model_config)
        self.my_dir = os.path.dirname(__file__)
        self.post_processors = {}
        for field_name in pp_config.keys():
            self.post_processors[field_name] = self.init_processor(pp_config[field_name])

  
    def init_processor(self, config):
        if config['type'] == 'Greed_LM':
            return Greed_LM()
        elif config['type'] == 'Date_LM':
            return Date_LM(config['max_words'])
        elif config['type'] == 'Time_LM':
            return Time_LM(config['max_words'])
        elif config['type'] == 'Money_LM':
            return Money_LM(config['max_words'])
        elif config['type'] == 'Reciept_id_LM':
            return Receipt_id_LM(config['max_words'])
        elif config['type'] == 'Quantity_LM':
            return Quantity_LM(config['max_words'])
        elif config['type'] == 'Pos_id_LM':
            return Pos_id_LM(config['max_words'])
        elif config['type'] == 'Product_id_LM':
            return Product_id_LM(config['max_words'])
        elif config['type'] == 'Receipt_id_LM':
            return Receipt_id_LM()
        elif config['type'] == 'Martname_LM':
            return Martname_LM(os.path.join(self.my_dir, config['dict_path']), config['max_words'])

    
    def predict(self, request_id, info):
        result = info
        for key in info['raw_result'].keys():
            if key == 'products':
                products = []
                for raw_product in info['raw_result'][key]:
                    product = {}
                    for pd_key in raw_product.keys():
                        product[pd_key] = ''
                        if len(raw_product[pd_key]) != 0:
                            product[pd_key] = self.post_processors[pd_key].predict(None, None, None, raw_product[pd_key], info['charset_list'])[-1]
                    products.append(product)
                result['result'][key] = products
            else:
                result['result'][key] = ''
                if len(info['raw_result'][key]) != 0:
                    result['result'][key] = self.post_processors[key].predict(None, None, None, info['raw_result'][key], info['charset_list'])[-1]
        # add missing fields by rule
        # add mart name by pos_id
        if 'pos_id' in result['result'].keys() and ('mart_name' not in result['result'].keys() or result['result']['mart_name'] == ''):
            result['result']['mart_name'] = self.post_processors['mart_name'].predict(None, None, None, result['result']['pos_id'], info['charset_list'])[-1]
            result['result']['pos_id'] = result['result']['pos_id'][-2:]
        return result
