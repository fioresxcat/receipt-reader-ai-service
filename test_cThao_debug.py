import os
import cv2
import pdb
import unidecode
import fitz
import utils
import base64
import logging
import argparse
import numpy as np
from pathlib import Path
import json
import shutil
import Levenshtein
import logging.config
logging.config.fileConfig('configs/logging.conf')

# from reader import Reader
# from debugger import Debugger
from inpout import Input, Output


FIELD_MAPPING = {
    'name': 'mart_name',
    'receipt_number': 'receipt_id',
    'product_code': 'product_id',
    'product_amount': 'product_quantity',
}

GENERAL_FIELDS = ['mart_name', 'receipt_id', 'pos_id', 'date', 'time', 'staff', 'total_money', 'total_quantity']
PRODUCT_FIELDS = ['product_id', 'product_name', 'product_quantity', 'product_unit_price', 'product_total_money']


def str_similarity(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    score = 1 - (distance / (max(len(str1), len(str2))))
    return score


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
    normalize = False
    lower = True
    remove_space = False

    def preprocess_result(text):
        text = str(text)
        if text == '-':
            text = ''
        if normalize:
            text = unidecode.unidecode(text)
        if lower:
            text = text.lower()
        if remove_space:
            text = text.replace(' ', '')
        return text
    
    dirs = [
        # ('logs/v1.0.1/Go_2022_53', 'test_files/receipt_data-test_cThao_warped/Go_2022_53/label-Go-2022-53.json'),
        # ('logs/v1.0.1/BigC_2022_49', 'test_files/receipt_data-test_cThao_warped/BigC_2022_49/label-bigC-2022-49.json'),
        ('logs/v1.0.1/Coopmart_CoopXtra_2022_76', 'test_files/receipt_data-test_cThao_warped/Coopmart_CoopXtra_2022_76/label-coopmart-coopxtra-2022-76.json'),
        # ('logs/v1.0.1/Emart_2022_29', 'test_files/receipt_data-test_cThao_warped/Emart_2022_29/label-emart-2022-29.json'),
        # ('logs/v1.0.1/GS25_46', 'test_files/receipt_data-test_cThao_warped/GS25_46/label-gs25-46.json'),
        # ('logs/v1.0.1/Vinmart_50', 'test_files/receipt_data-test_cThao_warped/Vinmart_50/label-vinmart-50.json'),
        # ('logs/v1.0.1/Winmart_2022_40', 'test_files/receipt_data-test_cThao_warped/Winmart_2022_40/label-winmart-2022-38.json')
    ]

    # init field stats
    field_stats = {}
    for field in GENERAL_FIELDS + PRODUCT_FIELDS:
        field_stats[field] = {
            'accuracy': 0,
            'total': 0,
            'correct': 0,
        }

    for result_dir, label_fp in dirs:
        with open(label_fp) as f:
            labels = json.load(f)
        
        for fn in os.listdir(result_dir):  # chi tinh acc cho nhung file da chay xong
            # get gt
            try:
                file_anno = [lb for lb in labels if 'file' in lb and lb['file'] == fn][0]
            except Exception as e:
                raise e
                print(f'{fn} has no label')
                continue
            
            # format fields
            orig_fields = list(file_anno.keys())
            for orig_field in orig_fields:
                field = FIELD_MAPPING[orig_field] if orig_field in FIELD_MAPPING else orig_field
                if field not in GENERAL_FIELDS and field != 'products':
                    file_anno.pop(field)
                else:
                    file_anno[field] = file_anno.pop(orig_field)
                if field == 'products':
                    for index, prod_gt in enumerate(file_anno['products']):
                        # mapping field
                        prod_fields = list(prod_gt.keys())
                        for prod_field in prod_fields:
                            mapped_field = FIELD_MAPPING[prod_field] if prod_field in FIELD_MAPPING else prod_field
                            prod_gt[mapped_field] = prod_gt.pop(prod_field)
                        # remove non-extracted fields
                        prod_gt = {k:v for k,v in prod_gt.items() if k in PRODUCT_FIELDS}
                        file_anno['products'][index] = prod_gt

            print(f'Processing {fn} ...')
            # get pred
            pred_fp = os.path.join(result_dir, fn, 'result.json')
            if not os.path.exists(pred_fp):
                continue
            with open(pred_fp) as f:
                file_pred = json.load(f)

            for field in file_anno:
                if field not in GENERAL_FIELDS and field != 'products':
                    continue

                if field in GENERAL_FIELDS:
                    gt = file_anno[field]
                    pred = file_pred[field] 
                    field_stats[field]['total'] += 1
                    field_stats[field]['correct'] += int(preprocess_result(gt)==preprocess_result(pred))

                elif field == 'products':
                    for i, prod_gt in enumerate(file_anno['products']):
                        for prod_field in prod_gt.keys():
                            field_stats[prod_field]['total'] += 1

                        # find prod with most similar name
                        final_prod = None
                        max_sim = 0
                        for pred_prod in file_pred['products']:
                            sim = str_similarity(pred_prod['product_name'].lower(), prod_gt['product_name'].lower())
                            if sim > max_sim and sim > 0.7:
                                max_sim = sim
                                final_prod = pred_prod
                        if final_prod is not None:
                            for prod_field, gt_field_value in prod_gt.items():
                                pred_field_value = final_prod[prod_field]
                                field_stats[prod_field]['correct'] += int(preprocess_result(gt_field_value)==preprocess_result(pred_field_value))
                    
    # compute acc
    for field in field_stats.keys():
        if field_stats[field]['total'] == 0:
            continue
        field_stats[field]['accuracy'] = round(field_stats[field]['correct'] / field_stats[field]['total'], 4)
    for field, field_info in field_stats.items():
        print(f'{field}: {field_info}')



if __name__ == '__main__':
    pass
    compute_acc()
    # check_error()
    # get_err_files()
    # process_log_aDung()