import os
import re
import cv2
import pdb
import json
import base64

from inpout import Input, Output
from utils.redis import to_redis, from_redis, remove_key_redis
from utils.utils import base64_to_image, list_base64_to_images


class BasicHandler(object):
    def __init__(self, method_processors, redis_db, time_to_expire_s):
        self.method_processors = method_processors
        self.redis_db = redis_db
        self.time_to_expire_s = int(time_to_expire_s)
        
        
    def format_metadata(self, metadata):
        new_metadata = []
        for key in metadata.keys():
            new_metadata.append({
                'model_name': key,
                'num_request': metadata[key]['num_request'],
                'total_batch_size': metadata[key]['total_batch_size']
            })
        return new_metadata



class AppcheckHandler(BasicHandler):
    def __init__(self, reader, redis_db, time_to_expire_s):
        super(AppcheckHandler, self).__init__(reader, redis_db, time_to_expire_s)
      

    def format(self, request_id, data):
        formated_data = {
            "rule_code": data['rule_code'],
            "rule_msg": data['rule_msg'],
        }
        error = {'error_code': 0, 'error_msg': 'OK'}
        if len(data['rule_code']) == 0:
            formated_data['is_pass'] = True
        else:
            formated_data['is_pass'] = False
        # save images to redis
        if 'rotated_images' in data.keys():
            log_data = []
            for i, rotated_image in enumerate(data['rotated_images']):
                base64_image = base64.b64encode(cv2.imencode('.jpg', rotated_image)[1].tostring())
                log_data.append((request_id + '_rotatedimage:' + str(i), base64_image))
            log_data.append((request_id + '_num_images', str(len(data['rotated_images']))))
            log_data.append((request_id + '_paper_type', str(data['paper_type'])))
            error = to_redis(log_data, self.redis_db, self.time_to_expire_s)
        return error, formated_data

    
    def process(self, request_id, list_b64_images):
        # load image
        images = list_base64_to_images(list_b64_images)
        formated_data = {}
        error = {'error_code': 0, 'error_msg': 'OK'}
        metadata = {}
        inp = Input(data={'images': images})
        raw_data, metadata = self.method_processors.methods['AppCheck'].predict(request_id, inp)
        error = raw_data.get_error()
        if error['error_code'] == 0:
            error, formated_data = self.format(request_id, raw_data.get_data())
        metadata = self.format_metadata(metadata)
        # return 
        return error, formated_data, metadata

    
    
class OCRHandler(BasicHandler):
    def __init__(self, method_processors, redis_db, time_to_expire_s):
        super(OCRHandler, self).__init__(method_processors, redis_db, time_to_expire_s)
        self.method_processors = method_processors


    def format(self, request_id, data):
        formated_data = {
            "error_code": data['rule_code'],
            "error_msg": data['rule_msg'],
        }
        for key in data['result'].keys():
            if key == 'mart_name':
                formated_data['name'] = data['result'][key]
            elif key == 'tax_code':
                formated_data['tax_number'] = data['result'][key]
            elif key == 'receipt_id':
                formated_data['receipt_number'] = data['result'][key]
            elif key == 'products':
                new_products = []
                for product in data['result'][key]:
                    new_product = {}
                    for p_key in product:
                        if p_key == 'product_quantity':
                            new_product['product_amount'] = product[p_key]
                        elif p_key == 'product_id':
                            new_product['product_code'] = product[p_key]
                        elif 'price' in p_key or 'money' in p_key:
                            new_product[p_key] = re.sub('(\.\d{2}$)|[^\d|\-]', '', product[p_key])
                        else:
                            new_product[p_key] = product[p_key]
                    new_products.append(new_product)
                formated_data[key] = new_products
            elif 'price' in key or 'money' in key:
                formated_data[key] = re.sub('(\.\d{2}$)|[^\d|\-]', '', data['result'][key])
            else:
                formated_data[key] = data['result'][key]
        return formated_data
        
        
    def process(self, request_id):
        # init output
        formated_data = {}
        error = {'error_code': 0, 'error_msg': 'OK'}
        metadata = {}
        # load images in redis
        error, rotated_images, paper_type = from_redis(self.redis_db, request_id)
        # process each type
        if error['error_code'] == 0:
            if paper_type == 'receipt':
                inp = Input(data={'rotated_images': rotated_images})
                raw_data, metadata = self.method_processors.methods['OCR'].predict(request_id, inp)
            else:
                inp = Input(data={'rotated_images': rotated_images})
                raw_data, metadata = self.method_processors.methods['OCRA4'].predict(request_id, inp)
            error = raw_data.get_error()
            if error['error_code'] == 0:
                formated_data = self.format(request_id, raw_data.get_data())
                _ = remove_key_redis(self.redis_db, request_id)
        metadata = self.format_metadata(metadata)
        # return 
        return error, formated_data, metadata
    
    
