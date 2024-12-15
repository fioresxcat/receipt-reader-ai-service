import os
import pdb
import cv2
import numpy as np
from PIL import Image

from .base_ocr import BaseOCR
from utils.utils import total_time


class BarcodeOCR(BaseOCR):
    instance = None
    
    def __init__(self, common_config, model_config):
        super(BarcodeOCR, self).__init__(common_config, model_config)
        
        
    @staticmethod
    def get_instance(common_config, model_config):
        if BarcodeOCR.instance is None:
            BarcodeOCR.instance = BarcodeOCR(common_config, model_config)
        return BarcodeOCR.instance