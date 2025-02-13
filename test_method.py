import os
import cv2
import time
import pdb
import json
import utils
import base64
import logging
import argparse
import numpy as np
from pathlib import Path
import logging.config
logging.config.fileConfig('configs/logging.conf')

from datetime import datetime

from debugger import Debugger
from inpout import Input, Output
from methods import MethodProcessor

# load config
root_logger = logging.getLogger('root')
time_logger = logging.getLogger('time')
config_env = utils.load_yaml('configs/config_env.yaml')
config_methods = utils.load_yaml('configs/config_methods.yaml')
config_models = utils.load_yaml('configs/config_models.yaml')
config_common = utils.load_yaml('configs/config_common.yaml')
pdb.set_trace()

list_mart_types = ['coopmart', 'emart', 'gs25', 'newbigc_go_top', 'winmart_combined']


def is_image(fp):
    fp = str(fp)
    return fp.endswith('.jpg') or fp.endswith('.png') or fp.endswith('.jpeg') or fp.endswith('.JPG') or fp.endswith('.JPEG') or fp.endswith('.PNG')




def main_multi_dir(args):
    log_path = args.log_path
    debugger = Debugger(log_path=log_path)
    method_processors = MethodProcessor(config_env, config_methods, config_models, root_logger, time_logger, debugger)
    dirs = [
        'test_files/receipt_data-test_warped/BigC_2022_49',
        'test_files/receipt_data-test_warped/Coopmart_CoopXtra_2022_76',
        'test_files/receipt_data-test_warped/Emart_2022_29',
        'test_files/receipt_data-test_warped/Go_2022_53',
        'test_files/receipt_data-test_warped/GS25_46',
        'test_files/receipt_data-test_warped/Winmart_2022_40'
    ]
    files = []
    for dir in dirs:
        files.extend([fp for fp in Path(dir).glob('*') if is_image(fp)])
    print('NUMBER OF FILES: ', len(files))
    err_files = []
    for i, file in enumerate(files):
        # if file != 'gs25-1.jpg':
        #     continue
        try:
            mart_type = args.mart_type if args.mart_type else Path(file).parent
            # assert mart_type in list_mart_types
            # file = 'img-2.jpeg'
            print('PROCESSING: ', file)
            if '.json' in file or 'HEIC' in file or '.DS_Store' in file or not is_image(file):
                continue
            # file_path = os.path.join(args.inp_path, file)
            file_path = str(file)
            images = []
            if os.path.isdir(file_path):
                sub_files = os.listdir(file_path)
                sub_files.sort()
                for sub_file in sub_files:
                    with open(os.path.join(file_path, sub_file), "rb") as image_file:
                        base64_string = base64.b64encode(image_file.read())
                    nparr = np.fromstring(base64.b64decode(base64_string), np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    images.append(image)
            else:
                with open(file_path, "rb") as image_file:
                    base64_string = base64.b64encode(image_file.read())
                nparr = np.fromstring(base64.b64decode(base64_string), np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                images.append(image)
            # gen request
            inp = Input(data = {'rotated_images': images, 'mart_type': mart_type})
            if args.inp_type == 'ocr':
                out, metadata = method_processors.methods['OCR'].predict(file, inp)
            elif args.inp_type == 'ocr_llm':
                out, metadata = method_processors.methods['OCR_LLM'].predict(file, inp)
            if out.get_error()['error_code'] != 0:
                with open(os.path.join(log_path, file, 'error.json'), 'w') as f:
                    json.dump(out.get_error(), f)
                print(out.get_data()['mart_type'])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise e
            print(e)
            err_files.append(file)
            continue
        
    print('NUMBER OF ERR FILES: ', len(err_files))
    for file in err_files:
        print(file)



def main(args):
    log_path = args.log_path
    debugger = Debugger(log_path=log_path)
    method_processors = MethodProcessor(config_env, config_methods, config_models, root_logger, time_logger, debugger)
    files = os.listdir(args.inp_path)
    print('NUMBER OF FILES: ', len(files))
    err_files = []
    ls_times= []
    for i, file in enumerate(files):
        if file != 'emart-1.jpg':
            continue
        try:
            mart_type = args.mart_type if args.mart_type else Path(file).parent
            # assert mart_type in list_mart_types
            # file = 'img-2.jpeg'
            print('PROCESSING: ', file)
            if '.json' in file or 'HEIC' in file or '.DS_Store' in file or not is_image(file):
                continue
            file_path = os.path.join(args.inp_path, file)
            images = []
            if os.path.isdir(file_path):
                sub_files = os.listdir(file_path)
                sub_files.sort()
                for sub_file in sub_files:
                    with open(os.path.join(file_path, sub_file), "rb") as image_file:
                        base64_string = base64.b64encode(image_file.read())
                    nparr = np.fromstring(base64.b64decode(base64_string), np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    images.append(image)
            else:
                with open(file_path, "rb") as image_file:
                    base64_string = base64.b64encode(image_file.read())
                nparr = np.fromstring(base64.b64decode(base64_string), np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                images.append(image)
            # gen request
            inp = Input(data = {'rotated_images': images, 'mart_type': mart_type})
            s = time.perf_counter()
            if args.inp_type == 'ocr':
                out, metadata = method_processors.methods['OCR'].predict(file, inp)
            elif args.inp_type == 'ocr_llm':
                out, metadata = method_processors.methods['OCR_LLM'].predict(file, inp)
            pdb.set_trace()
            ls_times.append(time.perf_counter() - s)
            print('TIME: ', time.perf_counter() - s)
            if out.get_error()['error_code'] != 0:
                with open(os.path.join(log_path, file, 'error.json'), 'w') as f:
                    json.dump(out.get_error(), f)
                print(out.get_data()['mart_type'])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise e
            print(e)
            err_files.append(file)
            continue
        
    print('NUMBER OF ERR FILES: ', len(err_files))
    for file in err_files:
        print(file)
    print('AVG TIME: ', np.mean(ls_times))
    print('TOTAL TIME: ', sum(ls_times))
    print('NUM FILE: ', len(ls_times))


        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inp_path', type=str, default='test_files/files')
    parser.add_argument('--inp_type', type=str, default='ocr')
    parser.add_argument('--log_path', default='logs/temp')
    parser.add_argument('--mart_type', default='emart')
    args = parser.parse_args()
    main(args)
    # main_multi_dir(args)