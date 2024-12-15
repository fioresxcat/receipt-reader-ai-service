import os
import sys
import cv2
import pdb
import time
import grpc
import glob
import json
import utils
import random
import base64
import imutils
from datetime import datetime

from grpc_classes import Scanit_OCRService_pb2, Scanit_OCRService_pb2_grpc


options = [
    ('grpc.max_receive_message_length', 1024 * 1024 * 1024),
    ('grpc.max_send_message_length', 1024 * 1024 * 1024)
]
# channel = grpc.insecure_channel("172.31.22.114:5000", options=options) # stag
# channel = grpc.insecure_channel("172.21.1.143:5000", options=options) # dev
channel = grpc.insecure_channel("0.0.0.0:5000", options=options)
stub = Scanit_OCRService_pb2_grpc.ScanitOCRServicesStub(channel)

files = glob.glob(os.path.join(sys.argv[1], '*'))
files.sort()
CHUNKSIZE = 1024 * 64
print('NUMBER OF FILES: ', len(files))
for index, file in enumerate(files):
    index = '123456789'
    print(file)
    # AppCheck request
    list_b64_images = []
    if os.path.isdir(file):
        sub_files = os.listdir(file)
        for sub_file in sub_files:
            with open(os.path.join(file, sub_file), "rb") as image_file:
                b64_image = base64.b64encode(image_file.read())
                list_b64_images.append(b64_image)
    else:
        with open(file, "rb") as image_file:
            b64_image = base64.b64encode(image_file.read())
            list_b64_images.append(b64_image)
    start = datetime.now()
    request = Scanit_OCRService_pb2.AppCheckRequest(request_id=str(index), images=list_b64_images)
    response = stub.AppCheck(request)
    json_resp = json.loads(response.json_data)
    print(response)
    print('APP: ', datetime.now() - start)
    # OCR request
    start = datetime.now()
    request = Scanit_OCRService_pb2.OCRRequest(request_id=str(index))
    response = stub.OCR(request)
    json_resp = json.loads(response.json_data)
    print(response)
    print('OCR: ', datetime.now() - start)
    

    






            
    


