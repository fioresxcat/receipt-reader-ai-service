import os
import re
import pdb
import json
import numpy as np

from json_repair import repair_json
from utils.utils import total_time
from modules.base_module import BaseModule


class Postprocessor(BaseModule):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(Postprocessor, self).__init__(common_config, model_config)
        self.my_dir = os.path.dirname(__file__)
        self.field_structure = {
            'general_info': {
                'mart_name': str,
                # 'phone': list,
                # 'address': str,
                # 'website': list,
                'pos_id': str,
                'receipt_id': str,
                'staff': str,
                'date': str,
                'time': str,
                # 'discount': str,
                'total_money': str,
                'total_quantity': str
            },
            'product_info': {
                'product_name': str,
                'product_id': str,
                'product_quantity': str,
                'product_unit_price': str,
                'product_total_money': str
            }
        }
        
        self.keep_fields = ['mart_name', 'date', 'receipt_id', 'pos_id', 'staff', 'time', 'total_money', 'total_quantity']
        self.product_keep_fields = ['product_id', 'product_name', 'product_unit_price', 'product_quantity', 'product_total_money']

        
    @staticmethod
    def get_instance(common_config, model_config):
        if Postprocessor.instance is None:
            Postprocessor.instance = Postprocessor(common_config, model_config)
        return Postprocessor.instance


    @total_time
    def predict(self, request_id, inp, out, metadata):
        inp_data = inp.get_data()
        raw_result = inp_data['raw_result']
        raw_result = repair_json(raw_result)
        raw_result = json.loads(raw_result)
        result = []
        
        if type(raw_result) is dict:
            ocr_cands = {}
            # add general info
            for key in self.field_structure['general_info'].keys():
                if key in raw_result.keys():
                    if type(raw_result[key]) == self.field_structure['general_info'][key]:
                        ocr_cands[key] = []
                        if type(raw_result[key]) == str:
                            if raw_result[key] == '-':
                                ocr_cands[key].append('')
                            else:
                                ocr_cands[key].append(raw_result[key])
                        elif type(raw_result[key]) == list:
                            for val in raw_result[key]:
                                if val == '-':
                                    ocr_cands[key].append('')
                                else:
                                    ocr_cands[key].append(val)
            if len(ocr_cands) != 0:
                ocr_cands = {k:v for k, v in ocr_cands.items() if k in self.keep_fields}
                result.append({
                    'group_name': 'general_info',
                    'infos': ocr_cands
                })

            # add provider_info, receiving_officer_info, feedback_info
            if 'product_info' in raw_result.keys():
                if type(raw_result['product_info']) is list:
                    for group_info in raw_result['product_info']:
                        ocr_cands = {}
                        has_value = False
                        # add sub info
                        for key in self.field_structure['product_info'].keys():
                            if key in group_info.keys():
                                if type(group_info[key]) == self.field_structure['product_info'][key]:
                                    ocr_cands[key] = []
                                    if type(group_info[key]) == str:
                                        if group_info[key] in ['', '-']:
                                            ocr_cands[key].append('')
                                        else:
                                            has_value = True
                                            ocr_cands[key].append(group_info[key])
                                    elif type(group_info[key]) == list:
                                        for val in group_info[key]:
                                            if val in ['', '-']:
                                                ocr_cands[key].append('')
                                            else:
                                                has_value = True
                                                ocr_cands[key].append(val)
                        if len(ocr_cands) != 0 and has_value:
                            ocr_cands = {k:v for k, v in ocr_cands.items() if k in self.product_keep_fields}
                            result.append({
                                'group_name': 'product_info',
                                'infos': ocr_cands
                            })
        
        metadata = self.add_metadata(metadata, 1, 1)
        out.set_data(result)
        return out, metadata
