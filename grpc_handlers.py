import os
import cv2
import pdb
import json
import io
import base64
import tritonclient.grpc as grpcclient

from inpout import Input, Output
from utils.redis import to_redis, load_images_from_redis, remove_key_redis
from utils.utils import base64_to_image, image_to_base64


class BasicHandler(object):
    def __init__(self, processor, redis_db, redis_ttl):
        self.processor = processor
        self.redis_db = redis_db
        self.redis_ttl = int(redis_ttl)
        
        
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
    def __init__(self, processor, redis_db, redis_ttl):
        super(AppcheckHandler, self).__init__(processor, redis_db, redis_ttl)
      

    def format(self, request_id, data):
        formated_data = data
        return formated_data
    

    def process(self, json_payload):
        # load request data
        request_id = json_payload['request_id']
        b64_images = json_payload['images']
        images = []
        for b64_im in b64_images:
            image = base64_to_image(b64_im.encode())
            images.append(image)

        # init output
        err_code = 0
        formated_data = {}
        metadata = {}

        # process
        inp = Input(data={'images': images})
        raw_data, metadata = self.processor.methods['AppCheck'].predict(request_id, inp)
        err_code = raw_data.get_error()
        if err_code == 0:
            formated_data = self.format(request_id, raw_data.get_data())
        
        # cache images to redis
        log_data = []
        for i, im in enumerate(images):
            b64_im = image_to_base64(im)
            log_data.append((f'{request_id}-raw_image-{i}', b64_im))
        log_data.append((f'{request_id}-num_images', len(images)))
        err_code = to_redis(self.processor.root_logger, log_data, self.redis_db, self.redis_ttl)
        
        metadata = self.format_metadata(metadata)
        return err_code, formated_data, metadata

    
    
class OCRHandler(BasicHandler):
    def __init__(self, method_processors, redis_db, redis_ttl):
        super(OCRHandler, self).__init__(method_processors, redis_db, redis_ttl)
        self.method_processors = method_processors


    def format(self, request_id, data):
        return data
        
        
    def process(self, json_payload):
        # init output
        formated_data = {}
        err_code = 0
        metadata = {}

        # load request data
        request_id = json_payload['request_id']

        # load images form request_id
        images = []
        err_code, images = load_images_from_redis(self.processor.root_logger, self.redis_db, request_id)
        if err_code != 0 and 'images' in json_payload and len(json_payload['images']) > 0:
            b64_images = json_payload['images']
            images = []
            for b64_im in b64_images:
                image = base64_to_image(b64_im.encode())
                images.append(image)
        mart_type = json_payload['mart_type']

        if len(images) > 0:
            inp = Input(data={'rotated_images': images, 'mart_type': mart_type})
            raw_data, metadata = self.method_processors.methods['OCR'].predict(request_id, inp)
            err_code = raw_data.get_error()
            if err_code == 0:
                formated_data = self.format(request_id, raw_data.get_data())

        metadata = self.format_metadata(metadata)
        return err_code, formated_data, metadata
    


class PingHandler:
    def __init__(self, root_logger):
        self.root_logger = root_logger
    
    def process(self):
        formated_data = 'PONG'
        error_code = 0
        metadata = {}
        return error_code, formated_data, metadata
    


class PingModelHandler:
    def __init__(self, root_logger, config_env):
        self.root_logger = root_logger
        self.triton_client = grpcclient.InferenceServerClient(url=config_env['inference_server']['ip'] + ':' + str(config_env['inference_server']['port']), ssl=False) 


    def process(self):
        error_code = 0
        formated_data = 'PONG'
        metadata = {}

        # Perform the health check
        try:
            # Check the server's health
            is_live = self.triton_client.is_server_live()
            self.root_logger.info(f"Inference server is live: {is_live}")

            is_ready = self.triton_client.is_server_ready()
            self.root_logger.info(f"Inference server is ready: {is_ready}")

            if not (is_live and is_ready):
                formated_data = 'CLOSE'
                error_code = 101

        except Exception as e:
            self.root_logger.info(f"Inference server health check failed: {e}")
            formated_data = 'CLOSE'
            error_code = 101
        
        return error_code, formated_data, metadata
