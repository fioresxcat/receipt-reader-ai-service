import os
import pdb
import cv2
import math
import copy
import numpy as np
from bpemb import BPEmb

from .utils import *
from utils.utils import total_time, load_yaml
from modules.base_module import BaseModule
from .base_information_extractor import BaseInformationExtractor



class InformationExtractor(BaseModule):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(InformationExtractor, self).__init__(common_config, model_config)
        self.my_dir = os.path.dirname(__file__)
        self.config = load_yaml(os.path.join(self.my_dir, 'config.yaml'))
        self.label_list = [
            'text', 'mart_name', 'receipt_id', 'pos_id', 'staff', 'date', 'time', 'product_id', 'product_name', 
            'product_unit_price', 'product_quantity', 'product_total_money', 'total_money', 'total_quantity'
        ]
        self.extractor = BaseInformationExtractor(common_config, model_config, self.label_list)


    @staticmethod
    def get_instance(common_config, model_config):
        if InformationExtractor.instance is None:
            InformationExtractor.instance = InformationExtractor(common_config, model_config)
        return InformationExtractor.instance


    @total_time
    def predict(self, request_id, inp, out, metadata):
        inp_data = inp.get_data()
        out, metadata = self.extractor.predict(request_id, inp, out, metadata)
        metadata = self.add_metadata(metadata, 1, 1)
        return out, metadata
        
        