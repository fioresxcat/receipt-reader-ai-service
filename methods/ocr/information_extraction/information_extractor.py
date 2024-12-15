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
        self.word_encoder = BPEmb(lang='vi', vs=10000, dim=300)
        self.mapping = {
            '711': 'seven_eleven',
            'aeon': 'aeon',
            'aeoncitimart': 'aeon_citimart',
            'bhx': 'bach_hoa_xanh',
            'bhx_2024': 'bhx_2024',
            'bhd': 'bhd',
            'brg': 'brg',
            'bitis': 'bitis',
            'bonchon': 'bonchon',
            'bsmart': 'bsmart',
            'cheers': 'cheers',
            'circlek': 'circlek',
            'coopfood': 'coopfood',
            'coopmart': 'coopmart',
            'dmx': 'dmx',
            'don_chicken': 'don_chicken',
            'emart': 'emart',
            'family_mart': 'family_mart',
            'fujimart': 'fujimart',
            'galaxy_cinema': 'galaxy_cinema',
            'globalx': 'globalx',
            'go': 'go',
            'gs25': 'gs25',
            'guardian': 'guardian',
            'hc': 'home_center',
            'heineken': 'heineken',
            'heineken_2024': 'heineken_2024',
            'kfc': 'kfc',
            'kingfood': 'kingfood',
            'lamthao': 'lamthao',
            'lanchi': 'old_bigc',
            'launuongmai': 'launuongmai',
            'lotte': 'lotte',
            'lotte_cinema': 'lotte_cinema',
            'lotteria': 'lotteria',
            'mega': 'mega',
            'ministop': 'ministop',
            'new_bigc': 'new_bigc',
            'new_gs25': 'new_gs25',
            'nguyenkim': 'nguyenkim',
            'nova': 'nova',
            'nuty': 'nuty',
            'okono': 'okono',
            'old_bigc': 'old_bigc',
            # 'pharmacity': 'pharmacity',
            'pepper_lunch': 'pepper_lunch',
            'pizza_company': 'pizza_company',
            'satra': 'satra',
            'sayaka': 'sayaka',
            'sukiya': 'sukiya',
            'tgsf': 'the_gioi_skin_food',
            'thegioisua': 'the_gioi_sua',
            'tiemlaunho': 'tiemlaunho',
            'topmarket': 'top',
            'umyoshi': 'umyoshi',
            'vinmart': 'winmart',
            'vinmartplus': 'winmart',
            'winlife': 'winmart'
        }
        self.extractor = {}
        for key in self.mapping.keys():
            self.extractor[key] = BaseInformationExtractor(common_config, model_config['information_extraction_' + self.config[self.mapping[key]]['model_name']], self.word_encoder, self.config[self.mapping[key]]['label_list'])


    @staticmethod
    def get_instance(common_config, model_config):
        if InformationExtractor.instance is None:
            InformationExtractor.instance = InformationExtractor(common_config, model_config)
        return InformationExtractor.instance


    @total_time
    def predict(self, request_id, inp, out, metadata):
        inp_data = inp.get_data()
        if inp_data['mart_type'] in self.mapping.keys():
            out, metadata = self.extractor[inp_data['mart_type']].predict(request_id, inp, out, metadata)
            metadata = self.add_metadata(metadata, 1, 1)
        else:
            out.set_error(102, 'input mart type not supported')
            out.set_data(inp.get_data())
        return out, metadata
        
        