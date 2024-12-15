import os
import pdb
import cv2
import numpy as np
from PIL import Image

from utils.utils import total_time
from modules.base_module import BaseModule
from modules.ocr.parseq.general_ocr import GeneralOCR


class OCR(BaseModule):
    instance = None
    
    def __init__(self, common_config, model_config):
        super(OCR, self).__init__(common_config, model_config)
        self.general_ocr = GeneralOCR.get_instance(common_config, model_config['general_ocr'])
        
        
    @staticmethod
    def get_instance(common_config, model_config):
        if OCR.instance is None:
            OCR.instance = OCR(common_config, model_config)
        return OCR.instance
    
    
    @total_time
    def predict(self, request_id, inp, out, metadata):
        result = inp.get_data()
        metadata[self.general_ocr.__class__.__name__] = {'num_request': 0, 'total_batch_size': 0}
        
        result['list_raw_words'] = []
        result['list_raw_cands'] = []
        
        for i in range(len(result['list_list_boxes'])):
            raw_words, raw_cands = self.general_ocr.predict_batch(result['list_list_boxes'][i], metadata)
            result['list_raw_words'].append(raw_words)
            result['list_raw_cands'].append(raw_cands)
        result['charset_list'] = self.general_ocr.charset_list
        out.set_data(result)
        return out, metadata