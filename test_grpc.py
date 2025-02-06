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

from grpc_classes import ReceiptOCRService_pb2, ReceiptOCRService_pb2_grpc


def is_image(fp):
    fp = str(fp)
    return fp.endswith('.jpg') or fp.endswith('.png') or fp.endswith('.jpeg') or fp.endswith('.JPG') or fp.endswith('.JPEG') or fp.endswith('.PNG')


options = [
    ('grpc.max_receive_message_length', 1024 * 1024 * 1024),
    ('grpc.max_send_message_length', 1024 * 1024 * 1024)
]
channel = grpc.insecure_channel("0.0.0.0:5001", options=options)
stub = ReceiptOCRService_pb2_grpc.ReceiptOCRServicesStub(channel)

def main(args):
    # get files
    files = os.listdir(args.inp_path)
    files.sort()
    err_files = []
    for i, fn in enumerate(files):
        if fn != 'emart-1.jpg':
            continue
        try:
            print('PROCESSING: ', fn)
            if not is_image(fn):
                continue
            file_path = os.path.join(args.inp_path, fn)
            b64_images = []
            with open(file_path, "rb") as image_file:
                base64_string = base64.b64encode(image_file.read()).decode()
            b64_images.append(base64_string)

            # app check
            payload_dict = {
                'request_id': fn,
                'images': b64_images
            }
            payload = json.dumps(payload_dict)
            request = ReceiptOCRService_pb2.ReceiptOCRRequest(action='APPCHECK', payload=payload)
            response = stub.ReceiptOCR(request)
            code = response.code
            data = json.loads(response.data)
            metadata = json.loads(response.metadata)
            print(f'Code: {code}, Appcheck Result: {data}')
            # pdb.set_trace()

            # ocr
            payload_dict = {
                'request_id': fn,
                'images': [],
                'mart_type': args.mart_type
            }
            payload = json.dumps(payload_dict)
            request = ReceiptOCRService_pb2.ReceiptOCRRequest(action='OCR', payload=payload)
            response = stub.ReceiptOCR(request)
            code = response.code
            data = json.loads(response.data)
            metadata = json.loads(response.metadata)
            print(f'Code: {code}, OCR Result: {data}')
            pdb.set_trace()

        except KeyboardInterrupt:
            raise

        except Exception as e:
            raise e
            print(e)
            err_files.append(fn)
            continue


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='input for testing grpc')
    parser.add_argument('--inp_path', type=str, required=True)
    parser.add_argument('--mart_type', type=str, required=True)
    args = parser.parse_args()
    main(args)