import os
import pdb
import cv2
import numpy as np 

from modules.base_module import BaseModule
from .pp_config import pp_config
from .rules import *


class PostProcessorWINMART(BaseModule):
    def __init__(self, common_config, model_config):
        super(PostProcessorWINMART, self).__init__(common_config, model_config)
        self.my_dir = os.path.dirname(__file__)
        self.post_processors = {}
        for field_name in pp_config.keys():
            self.post_processors[field_name] = self.init_processor(pp_config[field_name])


    def init_processor(self, config):
        if config['type'] == 'Value_LM':
            return Value_LM(os.path.join(self.my_dir, config['dict_path']), config['max_words'])
        if config['type'] == 'Martname_LM':
            return Martname_LM(os.path.join(self.my_dir, config['dict_path']), config['max_words'])
        if config['type'] == 'ProductName_LM':
            return ProductName_LM(os.path.join(self.my_dir, config['dict_path']), config['max_words'])
        elif config['type'] == 'Greed_LM':
            return Greed_LM()
        elif config['type'] == 'Counter_id_LM':
            return Counter_id_LM(config['max_words'])
        elif config['type'] == 'Staff_LM':
            return Staff_LM(config['max_words'])
        elif config['type'] == 'Date_LM':
            return Date_LM(config['max_words'])
        elif config['type'] == 'Time_LM':
            return Time_LM(config['max_words'])
        elif config['type'] == 'Receipt_id_LM':
            return Receipt_id_LM(config['max_words'])
        elif config['type'] == 'Product_id_LM':
            return Product_id_LM(config['max_words'])
        elif config['type'] == 'Money_LM':
            return Money_LM(config['max_words'])
        elif config['type'] == 'VAT_LM':
            return VAT_LM(config['max_words'])
        elif config['type'] == 'Discount_Money_LM':
            return Discount_Money_LM(config['max_words'])
        elif config['type'] == 'Quantity_LM':
            return Quantity_LM()


    def predict(self, request_id, info):
        result = info
        for key in info['raw_result'].keys():
            if key == 'products':
                products = []
                for raw_product in info['raw_result'][key]:
                    product = {}
                    for pd_key in raw_product.keys():
                        product[pd_key] = ''
                        if pd_key == 'product_quantity':
                            product[pd_key] = '1'
                        if len(raw_product[pd_key]) != 0:
                            product[pd_key] = self.post_processors[pd_key].predict(None, None, None, raw_product[pd_key], info['charset_list'])[-1]
                    products.append(product)
                result['result'][key] = products
            else:
                result['result'][key] = ''
                if len(info['raw_result'][key]) != 0:
                    result['result'][key] = self.post_processors[key].predict(None, None, None, info['raw_result'][key], info['charset_list'])[-1]
        # pp bắt dính date và time
        if result['result']['date'] != '' and result['result']['time'] == '':
            result['result']['time'] = self.post_processors['time'].predict(None, None, None, info['raw_result']['date'], info['charset_list'])[-1]
        return result
