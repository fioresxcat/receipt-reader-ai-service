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
import multiprocessing

from tqdm import tqdm
from datetime import datetime
from grpc_classes import Scanit_OCRService_pb2, Scanit_OCRService_pb2_grpc


def send_request(files, i):
    time.sleep(i * 0.45)
    start = datetime.now()
    print('start: ', i)
    for index, file in enumerate(files):
        # AppCheck request
        with open(file, "rb") as image_file:
            b64_image = base64.b64encode(image_file.read())
        start = datetime.now()
        request = Scanit_OCRService_pb2.AppCheckRequest(request_id=str(i), image=b64_image)
        response = stub.AppCheck(request)
        # print(json.loads(response.json_data))
        # OCR request
        start = datetime.now()
        request = Scanit_OCRService_pb2.OCRRequest(request_id=str(i))
        response = stub.OCR(request)
        json_resp = json.loads(response.json_data)
        # print(json.loads(response.json_data))
    print('end: ', i, datetime.now() - start)


options = [
    ('grpc.max_receive_message_length', 1024 * 1024 * 1024),
    ('grpc.max_send_message_length', 1024 * 1024 * 1024)
]
channel = grpc.insecure_channel("0.0.0.0:5000", options=options)
stub = Scanit_OCRService_pb2_grpc.ScanitOCRServicesStub(channel)

files = glob.glob(os.path.join(sys.argv[1], '*'))
files.sort()
start = datetime.now()
num_workers = 200
list_p = []
for i in range(num_workers):
    p = multiprocessing.Process(target=send_request, args=(files[:1], i, ))
    p.start()
    list_p.append(p)

for p in list_p:
    p.join()
print(datetime.now() - start)

    






            
    


