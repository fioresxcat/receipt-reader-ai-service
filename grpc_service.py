import pdb
import sys
import cv2
import grpc
import time
import json
import redis
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf')

from datetime import datetime
from concurrent import futures
from redis.cluster import RedisCluster as Redis
from google.protobuf.json_format import ParseDict

from methods import MethodProcessor
from debugger import Debugger
from utils.utils import load_yaml
from grpc_service_handlers import *
from grpc_classes import Scanit_OCRService_pb2, Scanit_OCRService_pb2_grpc


# load config
root_logger = logging.getLogger('root')
time_logger = logging.getLogger('time')
config_env = load_yaml('configs/config_env.yaml')
config_methods = load_yaml('configs/config_methods.yaml')
config_models = load_yaml('configs/config_models.yaml')
config_common = load_yaml('configs/config_common.yaml')
# init redis client
if str(config_env['redis']['is_cluster']).lower() in ['0', 'false']:
    redis_db = redis.Redis(host=config_env['redis']['host'], port=config_env['redis']['port'], password=config_env['redis']['password'])
else:
    redis_db = Redis(host=config_env['redis']['host'], port=config_env['redis']['port'], password=config_env['redis']['password'])
# init debugger
debugger = None
if int(config_env['grpc']['DEBUG_MODE']) == 1:
    debugger = Debugger(log_path='logs')
# load method processors
method_processors = MethodProcessor(config_env, config_methods, config_models, root_logger, time_logger, debugger)
# load handlers
appcheck_handler = AppcheckHandler(method_processors, redis_db, config_env['redis']['time_to_expire_s'])
ocr_handler = OCRHandler(method_processors, redis_db, config_env['redis']['time_to_expire_s'])



class ScanitOCRServices(Scanit_OCRService_pb2_grpc.ScanitOCRServicesServicer):
    
    def AppCheck(self, request, context):
        start_time = time.time()
        # read request
        request_id = request.request_id
        list_b64_images = request.images
        # call corresponding handler
        error, json_data, metadata = appcheck_handler.process(request_id, list_b64_images)
        # format response
        response = Scanit_OCRService_pb2.AppCheckResponse()
        response.error.error_code = error['error_code']
        response.error.error_message = error['error_msg']
        response.json_data = json.dumps(json_data)
        response.metadata = json.dumps(metadata)
        # log result
        processing_time = time.time() - start_time
        root_logger.info('request_id={} action={} error_code="{}" processing_time={}\n'.format(request_id, 'AppCheck', error['error_code'], processing_time))
        return response

    def OCR(self, request, context):
        start_time = time.time()
        # read request
        request_id = request.request_id
        # call corresponding handler
        error, json_data, metadata = ocr_handler.process(request_id)
        # format response
        response = Scanit_OCRService_pb2.OCRResponse()
        response.error.error_code = error['error_code']
        response.error.error_message = error['error_msg']
        response.json_data = json.dumps(json_data)
        response.metadata = json.dumps(metadata)
        # log result
        processing_time = time.time() - start_time
        root_logger.info('request_id={} action={} error_code="{}" processing_time={}\n'.format(request_id, 'OCR', error['error_code'], processing_time))
        return response
    

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=int(config_env['grpc']['MAX_WORKERS'])),  options=[
        ('grpc.max_send_message_length', int(config_env['grpc']['MAX_MESSAGE_LENGTH'])),
        ('grpc.max_receive_message_length', int(config_env['grpc']['MAX_MESSAGE_LENGTH']))
    ])
    Scanit_OCRService_pb2_grpc.add_ScanitOCRServicesServicer_to_server(ScanitOCRServices(), server)

    print("Starting server. Listening on port " +str(config_env['grpc']['GRPC_PORT']))
    root_logger.info("Starting server. Listening on port " +str(config_env['grpc']['GRPC_PORT']))
    server.add_insecure_port('0.0.0.0:' + str(config_env['grpc']['GRPC_PORT']))
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    main()




