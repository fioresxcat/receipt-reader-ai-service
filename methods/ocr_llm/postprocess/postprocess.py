import os
import re
import pdb
import json
import numpy as np

from json_repair import repair_json
from utils.utils import total_time
from modules.base_module import BaseModule



class BaseMartPostprocessor:
    def __init__(self):
        pass


    def postprocess_general_fields(self, infos):
        return infos
    

    def postprocess_product_fields(self, infos):
        return infos


    def predict(self, result):
        for group_index, group in enumerate(result):
            if group['group_name'] == 'general_info':
                result[group_index]['infos'] = self.postprocess_general_fields(group['infos'])
            elif group['group_name'] == 'product_info':
                result[group_index]['infos'] = self.postprocess_product_fields(group['infos'])

        return result


    
class EmartPostprocessor(BaseMartPostprocessor):
    def postprocess_general_fields(self, infos):
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['pos_id', 'receipt_id', 'staff']:
                    if ':' in val:
                        new_val = ':'.join(val.split(':')[1:])
                        infos[field][val_index] = new_val
                elif field in ['date']:
                    infos[field][val_index] = val.replace('-', '/')
        return infos
    


class CoopmartPostprocessor(BaseMartPostprocessor):
    def format_money(self, raw_res):
        raw_words = raw_res.split(',')
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


    def postprocess_general_fields(self, infos):
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['pos_id', 'receipt_id', 'staff']:
                    if ':' in val:
                        new_val = ':'.join(val.split(':')[1:])
                        infos[field][val_index] = new_val
                elif field == 'total_money':
                    infos[field][val_index] = self.format_money(val)
        return infos
    

    def postprocess_product_fields(self, infos):
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['product_unit_price', 'product_total_money']:
                    infos[field][val_index] = self.format_money(val)
                elif field in ['product_quantity']:
                    infos[field][val_index] = val.replace('.', ',')
        return infos




class GS25Postprocessor(BaseMartPostprocessor):
    def __init__(self):
        self.my_dir = os.path.dirname(__file__)
        self.map = {}
        dict_path = os.path.join(self.my_dir, 'newgs25_names.txt')
        with open(dict_path, 'r', encoding='utf-8') as f:
            for row in f:
                mart_id, mart_name = row[:-1].split('\t')
                self.map[mart_id] = mart_name


    def map_mart_name(self, pos_id):
        s = re.search('VN\d{4}', pos_id)
        mart_name = ''
        mart_id = ''
        if s is not None:
            mart_id = s.group(0)
        if mart_id in self.map.keys():
            mart_name = self.map[mart_id]
        return mart_name
    

    def postprocess_general_fields(self, infos):
        mart_name = ''
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['receipt_id']:
                    if val.startswith('-'):
                        new_val = val[1:]
                        infos[field][val_index] = new_val
                elif field in ['pos_id']:
                    infos[field][val_index] = val[-2:]
                    mart_name = self.map_mart_name(val)
        infos['mart_name'] = [mart_name]
        return infos
    

    def postprocess_product_fields(self, infos):
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['product_unit_price', 'product_total_money']:
                    if '.' in val or ',' in val:
                        new_val = val.replace('.', ',')
                    else:
                        new_val = val + ',000'
                    val = val.replace('-', '')
                    infos[field][val_index] = new_val
                elif field in ['product_quantity']:
                    new_val = val.replace('-', '')
                    infos[field][val_index] = new_val
                    
        return infos
    



class NewBigCPostprocessor(BaseMartPostprocessor):
    def __init__(self):
        pass


    def postprocess_general_fields(self, infos):
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['total_money']:
                    infos[field][val_index] = val.replace('.', ',')
                    

        return infos
    

    def postprocess_product_fields(self, infos):
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['product_unit_price', 'product_total_money']:
                    infos[field][val_index] = val.replace('.', ',')
        return infos



class WinmartPostprocessor(BaseMartPostprocessor):
    def __init__(self):
        pass


    def postprocess_general_fields(self, infos):
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['time']:
                    num_digits = len([x for x in val if x.isdigit()])
                    if num_digits == 4:
                        new_val = val[:2] + ':' + val[-2:]
                        infos[field][val_index] = new_val

        return infos
    

    def postprocess_product_fields(self, infos):
        for field, values in infos.items():
            for val_index, val in enumerate(values):
                if field in ['product_unit_price', 'product_total_money']:
                    infos[field][val_index] = val.replace('.', ',')
        return infos
    



class LLMPostprocessor(BaseModule):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(LLMPostprocessor, self).__init__(common_config, model_config)
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
            'products': {
                'product_name': str,
                'product_id': str,
                'product_quantity': str,
                'product_unit_price': str,
                'product_total_money': str
            }
        }
        
        self.keep_fields = ['mart_name', 'date', 'receipt_id', 'pos_id', 'staff', 'time', 'total_money', 'total_quantity']
        self.product_keep_fields = ['product_id', 'product_name', 'product_unit_price', 'product_quantity', 'product_total_money']
        self.mart_postprocessors = {
            'emart': EmartPostprocessor(),
            'coopmart': CoopmartPostprocessor(),
            'gs25': GS25Postprocessor(),
            'new_bigc': NewBigCPostprocessor(),
            'winmart': WinmartPostprocessor(),
        }
        

    @staticmethod
    def get_instance(common_config, model_config):
        if LLMPostprocessor.instance is None:
            LLMPostprocessor.instance = LLMPostprocessor(common_config, model_config)
        return LLMPostprocessor.instance


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
            if 'products' in raw_result.keys():
                if type(raw_result['products']) is list:
                    for group_info in raw_result['products']:
                        ocr_cands = {}
                        has_value = False
                        # add sub info
                        for key in self.field_structure['products'].keys():
                            if key in group_info.keys():
                                if type(group_info[key]) == self.field_structure['products'][key]:
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

        final_result = self.mart_postprocessors[inp_data['mart_type']].predict(result)
        # pdb.set_trace()
        metadata = self.add_metadata(metadata, 1, 1)
        out.set_data(final_result)
        return out, metadata
