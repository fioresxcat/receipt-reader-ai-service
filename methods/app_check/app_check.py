import pdb
import cv2
import math
import numpy as np

from utils.utils import total_time
from modules.base_module import BaseModule

class AppCheck(BaseModule):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(AppCheck, self).__init__(common_config, model_config)
        
    
    @staticmethod
    def get_instance(common_config, model_config):
        if AppCheck.instance is None:
            AppCheck.instance = AppCheck(common_config, model_config)
        return AppCheck.instance


    @total_time
    def predict(self, request_id, inp, out, metadata):
        inp_data = inp.get_data()
        result = {}
        result['final_result'] = 'PASS'
        out.set_data(result)
        return out, metadata

    