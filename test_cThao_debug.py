import os
import cv2
import pdb
import fitz
import utils
import base64
import logging
import argparse
import numpy as np
from pathlib import Path
import json
import shutil

import logging.config
logging.config.fileConfig('configs/logging.conf')

# from reader import Reader
# from debugger import Debugger
from inpout import Input, Output


def process_log_aDung():
    dir = 'logs'
    out_dir = f'logs_ie/LCT-20'
    os.makedirs(out_dir, exist_ok=True)

    for pdf_name in os.listdir(dir):
        if pdf_name[-2] != '_':
            continue
        pdf_dir = os.path.join(dir, pdf_name)
        json_dir = os.path.join(pdf_dir, 'LCTInformationExtractor', 'output')

        for jp in Path(json_dir).glob('*.json'):
            img_fp = jp.with_suffix('.png')
            new_img_name = Path(img_fp).name.replace('page', pdf_name)
            shutil.copy(str(img_fp), os.path.join(out_dir, new_img_name))

            data = json.load(open(jp))
            data['imagePath'] = new_img_name

            new_jn = jp.name.replace('page', pdf_name)
            with open(os.path.join(out_dir, new_jn), 'w') as f:
                json.dump(data, f)

        print(f'Done {pdf_name}')



def check_error():
    # debugger = Debugger(log_path='logs/logs_B4_1.1.22_080424')
    # reader = Reader(config_env, config_methods, config_models, root_logger, time_logger, debugger)

    field2check = 'transfer_amount'
    
    # load err files
    with open('logs_file/Lenh-chuyen-tien-20/result_Lenh-chuyen-tien-20_0.0.7_20240913.json') as f:
        res = json.load(f)
    
    err_files = sorted([file['file'] for file in res['fields_acc']['info'][field2check]['failed']])
    err_files = list(set(err_files))
    fpaths = [os.path.join('logs_file/Lenh-chuyen-tien-20', fn.strip()) for fn in err_files]
    fpaths = [Path(fp) for fp in fpaths]
    print('NUMBER OF ERROR FILES: ', len(fpaths))

    # load label files
    with open('logs_file/Lenh-chuyen-tien-20/label-Lenh-chuyen-tien-20.json') as f:
        labels = json.load(f)
    print('Loaded labels!')

    log_dir = 'logs'
    for i, fp in enumerate(fpaths):
        # if 'CNBH 10' not in str(fp): continue
        if not os.path.exists(fp):
            print(f'{fp} NOT EXISTS!!!')
            pdb.set_trace()
            continue
        
        file = fp.name
        print('PROCESSING: ', fp)
        
        # load result
        result_path = os.path.join(log_dir, f'{file}_0', 'LCTOCRPostprocessor', 'output', 'log.json')
        result = json.load(open(result_path))

        try:
            cand = result[0]['infos'][0][field2check][0][0]
            pred = cand['cand']
            raw_pred = cand['raw_cand']
        except:
            pred = None
            raw_pred = None
    
        # load label
        file_labels = [lb for lb in labels if lb['file'] == file]
        if len(file_labels) == 0:
            print(f'{file} has no label')
            continue

        label = file_labels[0]
        true = label['data'][0]['info'][field2check]
        if pred != true:
            print(f'field: {field2check}, raw_pred: {raw_pred}, pred: {pred}, true: {true} ==> FALSE')
            pdb.set_trace()


def compute_acc():
    pass


if __name__ == '__main__':
    pass
    # check_error()
    # get_err_files()
    # process_log_aDung()