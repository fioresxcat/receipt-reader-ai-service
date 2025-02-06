import pdb
import grpc
import time
import json
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf')

from datetime import datetime
from concurrent import futures
from google.protobuf.json_format import ParseDict

import redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.exceptions import (
   BusyLoadingError,
   ConnectionError,
   TimeoutError
)

from methods.method_processor import MethodProcessor
from debugger import Debugger
from utils.utils import load_yaml
from utils.redis import check_redis_connection
from grpc_handlers import AppcheckHandler, OCRHandler, PingHandler, PingModelHandler
from grpc_classes import ReceiptOCRService_pb2, ReceiptOCRService_pb2_grpc


error_dict = {
    0: 'SUCCESS',
    -1: 'FAILED',
    201: 'Redis Write FAILED',
    202: 'Redis Read FAILED',
    203: 'Request ID not in Redis',
}

# load config
root_logger = logging.getLogger('root')
time_logger = logging.getLogger('time')
config_env = load_yaml('configs/config_env.yaml')
config_methods = load_yaml('configs/config_methods.yaml')
config_models = load_yaml('configs/config_models.yaml')

# init debugger
debugger = None
if int(config_env['grpc']['DEBUG_MODE']) == 1:
    debugger = Debugger(log_path='logs')

# load method processors
processor = MethodProcessor(config_env, config_methods, config_models, root_logger, time_logger, debugger)

# load redis
redis_use_ssl = str(config_env['redis']['use_ssl']).lower() not in ['0', 'false']
retry = Retry(ExponentialBackoff(), 3)
if str(config_env['redis']['is_cluster']).lower() in ['0', 'false']:
    redis_db = redis.Redis(
        host=str(config_env['redis']['host']), 
        port=str(config_env['redis']['port']), 
        password=str(config_env['redis']['password']), 
        ssl=redis_use_ssl,
        retry=retry,
        retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError]
    )
 
else:
    redis_db = redis.RedisCluster(
        host=str(config_env['redis']['host']), 
        port=str(config_env['redis']['port']), 
        password=str(config_env['redis']['password']),
        retry=retry, 
        cluster_error_retry_attempts=3, # Raise cluster error with TimeoutError or ConnectionError or ClusterDownError
    )

# check redis connection
connection_ok = check_redis_connection(redis_db)
if connection_ok:
    root_logger.info("Redis connection is OK at HOST: " + str(config_env['redis']['host']) + ', PORT: ' + str(config_env['redis']['port']))
else:
    raise SystemExit("Failed to connect to Redis at HOST:", str(config_env['redis']['host']), ', PORT: ', str(config_env['redis']['port']))


# load handlers
appcheck_handler = AppcheckHandler(processor, redis_db, config_env['redis']['time_to_expire_s'])
ocr_handler = OCRHandler(processor, redis_db, config_env['redis']['time_to_expire_s'])
ping_handler = PingHandler(root_logger)
ping_model_handler = PingModelHandler(root_logger, config_env)

# check model connection
code, json_data, metadata = ping_model_handler.process()
if json_data != "PONG":
    raise SystemExit("Failed to connect to inference server at HOST: " + str(config_env['inference_server']['ip']) + ', PORT: ' + str(config_env['inference_server']['port']))
else:
    root_logger.info('Inference server connection is OK at HOST: ' + str(config_env['inference_server']['ip']) + ', PORT: ' + str(config_env['inference_server']['port']))


class ReceiptOCRServices(ReceiptOCRService_pb2_grpc.ReceiptOCRServicesServicer):
    def ReceiptOCR(self, request, context):
        start_time = time.time()
        # read request
        action = request.action
        json_payload = json.loads(request.payload)
        request_id = json_payload['request_id']

        if action == 'PING':
            code, data, metadata = ping_handler.process()
            response = ReceiptOCRService_pb2.ReceiptOCRResponse()
            response.code = code
            response.data = json.dumps(data)
            response.metadata = json.dumps(metadata)
            return response
        elif action == 'APPCHECK':
            code, data, metadata = appcheck_handler.process(json_payload)
        elif action == 'OCR':
            code, data, metadata = ocr_handler.process(json_payload)
                
        # format response
        response = ReceiptOCRService_pb2.ReceiptOCRResponse()
        response.code = code
        response.data = json.dumps(data)
        response.metadata = json.dumps(metadata)

        # log result
        processing_time = time.time() - start_time
        root_logger.info('Request DONE, ' + error_dict[code], extra={
            'metadata': {
                'request_id': request_id,
                'action': action,
                'processing_time': processing_time,
            }
        })
        return response
    

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=int(config_env['grpc']['MAX_WORKERS'])),  options=[
        ('grpc.max_send_message_length', int(config_env['grpc']['MAX_MESSAGE_LENGTH'])),
        ('grpc.max_receive_message_length', int(config_env['grpc']['MAX_MESSAGE_LENGTH']))
    ])
    ReceiptOCRService_pb2_grpc.add_ReceiptOCRServicesServicer_to_server(ReceiptOCRServices(), server)

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




