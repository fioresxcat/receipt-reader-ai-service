import os
import pdb
import cv2
import numpy as np
from PIL import Image

from .base_ocr import BaseOCR
from utils.utils import total_time


class VATOCR(BaseOCR):
    instance = None
    
    def __init__(self, common_config, model_config):
        super(VATOCR, self).__init__(common_config, model_config)
        
        
    @staticmethod
    def get_instance(common_config, model_config):
        if VATOCR.instance is None:
            VATOCR.instance = VATOCR(common_config, model_config)
        return VATOCR.instance

