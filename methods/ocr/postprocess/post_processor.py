import os
import pdb
import cv2
import numpy as np

from modules.base_module import BaseModule
from utils.utils import total_time

from .post_process_coopmart.post_processor import PostProcessorCOOPMART
from .post_process_emart.post_processor import PostProcessorEMART
from .post_process_newbigc.post_processor import PostProcessorNEWBIGC
from .post_process_go.post_processor import PostProcessorGO
from .post_process_topmarket.post_processor import PostProcessorTOPMARKET
from .post_process_gs25.post_processor import PostProcessorGS25
from .post_process_newgs25.post_processor import PostProcessorNewGS25
from .post_process_vinmart.post_processor import PostProcessorVINMART
from .post_process_winmart.post_processor import PostProcessorWINMART



class PostProcessor(BaseModule):
    instance = None
    
    def __init__(self, common_config, model_config):
        super(PostProcessor, self).__init__(common_config, model_config)
        self.post_processor = {
            'coopmart': PostProcessorCOOPMART(common_config, model_config),
            'emart': PostProcessorEMART(common_config, model_config),
            'new_bigc': PostProcessorNEWBIGC(common_config, model_config),
            # 'go': PostProcessorGO(common_config, model_config),
            # 'topmarket': PostProcessorTOPMARKET(common_config, model_config),
            # 'vinmart': PostProcessorVINMART(common_config, model_config),
            # 'vinmartplus': PostProcessorWINMART(common_config, model_config),
            'winmart': PostProcessorWINMART(common_config, model_config),
            'gs25': PostProcessorGS25(common_config, model_config),
            # 'new_gs25': PostProcessorNewGS25(common_config, model_config),
            # 'winlife': PostProcessorVINMART(common_config, model_config)
        }

        self.keep_fields = ['mart_name', 'date', 'receipt_id', 'pos_id', 'staff', 'time', 'total_money', 'total_quantity', 'products']
        self.product_keep_fields = ['product_id', 'product_name', 'product_unit_price', 'product_quantity', 'product_total_money']


    @staticmethod
    def get_instance(common_config, model_config):
        if PostProcessor.instance is None:
            PostProcessor.instance = PostProcessor(common_config, model_config)
        return PostProcessor.instance
        

    @total_time
    def predict(self, request_id, inp, out, metadata):
        inp_data = inp.get_data()
        inp_data['result'] = {}
        result = self.post_processor[inp_data['mart_type']].predict(request_id, inp_data)
        # pdb.set_trace()
        metadata = self.add_metadata(metadata, 1, 1)
        # result['result']['type'] = inp_data['mart_type']
        # if result['result']['type'] in ['vinmart', 'vinmartplus']:
        #     if '+' in result['result']['mart_name'] and 'C+' not in result['result']['mart_name']:
        #         result['result']['type'] = 'winmartplus'
        #     else:
        #         result['result']['type'] = 'winmart'
        # elif result['result']['type'] in ['heineken', 'heineken_2024']:
        #     result['result']['type'] = 'heineken'
        
        result['result'] = {k: v for k, v in result['result'].items() if k in self.keep_fields}
        for product_index, product_info in enumerate(result['result']['products']):
            product_info = {k:v for k, v in product_info.items() if k in self.product_keep_fields}
            result['result']['products'][product_index] = product_info
            
        out.set_data(result)
        return out, metadata

