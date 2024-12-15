import os
import cv2
import pdb
import json
import utils
import base64
import logging
import argparse
import numpy as np
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


def main(args):
    log_path = args.log_path
    debugger = Debugger(log_path=log_path)
    method_processors = MethodProcessor(config_env, config_methods, config_models, root_logger, time_logger, debugger)
    files = os.listdir(args.inp_path)
    print('NUMBER OF FILES: ', len(files))
    for i, file in enumerate(files):
        # file = 'img-2.jpeg'
        print('PROCESSING: ', file)
        if '.json' in file or 'HEIC' in file or '.DS_Store' in file:
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
        inp = Input(data = {'images': images})
        # start = datetime.now()
        # run appcheck
        appcheck_out, metadata = method_processors.methods['AppCheck'].predict(file, inp)
        print('APPCHECK:')
        print(appcheck_out.get_data()['rule_code'])
        print(appcheck_out.get_data()['rule_msg'])
        
        # run ocr
        if 'rotated_images' in appcheck_out.get_data().keys():
            print('OCR:')
            # change image to jpg like in grpc service
            inp_data = appcheck_out.get_data()
            images = []
            for i in range(len(inp_data['rotated_images'])):
                base64_image = base64.b64encode(cv2.imencode('.jpg', inp_data['rotated_images'][i])[1].tostring())
                im_bytes = base64.b64decode(base64_image)
                im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
                image = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
                images.append(image)
            inp_data['rotated_images'] = images
            appcheck_out.set_data(inp_data)
            if appcheck_out.get_data()['paper_type'] == 'receipt':
                out, metadata = method_processors.methods['OCR'].predict(file, appcheck_out)
            else:
                out, metadata = method_processors.methods['OCRA4'].predict(file, appcheck_out)
            if out.get_error()['error_code'] != 0:
                with open(os.path.join(log_path, file, 'error.json'), 'w') as f:
                    json.dump(out.get_error(), f)
                print(out.get_data()['mart_type'])
            else:
                print(out.get_data()['mart_type'])
                print(out.get_data()['rule_code'])
                print(out.get_data()['rule_msg'])
        # print(datetime.now() - start)
        # break

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inp_path')
    parser.add_argument('--log_path', default='logs')
    args = parser.parse_args()
    main(args)