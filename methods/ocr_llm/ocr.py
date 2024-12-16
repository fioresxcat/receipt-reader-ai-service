import os
import pdb
import cv2
import numpy as np
from PIL import Image

from modules.base import BaseModule
from modules.ocr_parseq.short_ocr import ShortOCR
from modules.ocr_parseq.long_ocr import LongOCR
from utils.utils import total_time



class OCR(BaseModule):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(OCR, self).__init__(common_config, model_config)
        self.short_ocr = ShortOCR.get_instance(common_config, model_config['ocr_short'])
        self.long_ocr = LongOCR.get_instance(common_config, model_config['ocr_long'])
        self.my_dir = os.path.dirname(__file__)
        self.rate = 3
        

    @staticmethod
    def get_instance(common_config, model_config):
        if OCR.instance is None:
            OCR.instance = OCR(common_config, model_config)
        return OCR.instance
    

    @total_time
    def predict(self, request_id, inp, out, metadata):
        result = inp.get_data()
        short_list_images = []
        short_indexes = []
        long_list_images = []
        long_indexes = []
        
        for i, page_info in enumerate(result['pages']):
            page_info['raw_cands'] = []
            page_info['raw_words'] = []
            
            for j, (text_box_image, bb) in enumerate(zip(page_info['text_box_images'], page_info['text_boxes'])):
                xmin = min(bb[:, 0])
                xmax = max(bb[:, 0])
                ymin = min(bb[:, 1])
                ymax = max(bb[:, 1])
                w = xmax - xmin
                h = ymax - ymin
                if w / h <= self.rate:
                    short_list_images.append(text_box_image)
                    short_indexes.append((i, j))
                else:
                    long_list_images.append(text_box_image)
                    long_indexes.append((i, j))
                page_info['raw_cands'].append(None)
                page_info['raw_words'].append(None)
            # page_info.pop('text_box_images')
                
        metadata[self.short_ocr.__class__.__name__] = {
                    'num_request': 0,
                    'total_batch_size': 0
                }
        metadata[self.long_ocr.__class__.__name__] = {
                    'num_request': 0,
                    'total_batch_size': 0
                }
        
        short_list_raw_words, short_list_raw_cands = self.short_ocr.predict_batch([short_list_images], metadata)
        long_list_raw_words, long_list_raw_cands = self.long_ocr.predict_batch([long_list_images], metadata)
        for (i, j), raw_word, raw_cand in zip(short_indexes, short_list_raw_words[0], short_list_raw_cands[0]):
            result['pages'][i]['raw_words'][j] = raw_word
        for (i, j), raw_word, raw_cand in zip(long_indexes, long_list_raw_words[0], long_list_raw_cands[0]):
            result['pages'][i]['raw_words'][j] = raw_word

        result['charset_list'] = self.short_ocr.charset_list
        out.set_data(result)
        return out, metadata
