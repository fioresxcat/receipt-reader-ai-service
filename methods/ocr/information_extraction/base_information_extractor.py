import os
import re
import pdb
import cv2
import math
import copy
import numpy as np
from bpemb import BPEmb

from .utils import *
from utils.utils import total_time, load_yaml
from modules.base_module import BaseModule
from .lmv3_predictor import LayoutLMv3Predictor

class BaseInformationExtractor(BaseModule):
    def __init__(self, common_config, model_config, label_list):
        super(BaseInformationExtractor, self).__init__(common_config, model_config)
        self.general_fields = ['mart_name', 'tax_code', 'date', 'receipt_id', 'pos_id', 'staff', 'time', 'total_money', 'total_quantity', 'total_original_money', 'total_discount_money', 'barcode', 'mart_address', 'receipt_tax_number']
        self.product_fields = ['product_id', 'product_name', 'product_vat', 'product_quantity', 'product_unit_price', 'product_total_money', 'product_original_price', 'product_discount_money', 'product_total_original_money', 'product_discount_retail_money', 'product_discount_wholesale_money', 'second_product_name']
        # self.general_fields = []
        # for field in ['mart_name', 'tax_code', 'date', 'receipt_id', 'pos_id', 'staff', 'time', 'total_money', 'total_quantity', 'total_original_money', 'total_discount_money']:
        #     if field in self.label_list:
        #         self.general_fields.append(field)
        # self.product_fields = []
        # for field in ['product_id', 'product_name', 'product_vat', 'product_quantity', 'product_unit_price', 'product_total_money', 'product_original_price', 'product_discount_money']:
        #     if field in self.label_list:
        #         self.product_fields.append(field)
        self.lmv3 = LayoutLMv3Predictor(common_config, model_config, label_list)

    
    def get_sort_data(self, bbs, list_boxes, texts, cands):
        bb2text = dict(zip(bbs, texts))
        bb2cand = dict(zip(bbs, cands))
        bb2list_boxes = dict(zip(bbs, list_boxes))
        bb2idx_original = {x: idx for idx, x in enumerate(bbs)}   # theo thu tu truyen vao trong data['shapes']
        rbbs = row_bbs(copy.deepcopy(bbs))
        sorted_bbs = [bb for row in rbbs for bb in row]  # theo thu tu tu trai sang phai, tu tren xuong duoi
        bb2idx_sorted = {tuple(x): idx for idx, x in enumerate(sorted_bbs)}   # theo thu tu tu trai sang phai, tu tren xuong duoi
        sorted_indices = [bb2idx_sorted[bb] for bb in bb2idx_original.keys()]
        return bb2text, bb2cand, bb2list_boxes, rbbs, bb2idx_sorted, sorted_indices



    def get_raw_product_type1(self, field_start, field_end, field_spec, row_threshold, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels):
        """
        start by field_start
        end by field_end
        add field_spec to current product if exists
        """
        products_cand = []
        products_text = []
        product_list_boxes = []
        current_product_cand = None
        last_row_index = -1
        bb_index = 0
        for row_index, rbb in enumerate(rbbs):
            for bb in rbb:
                # fieldname = labels[bbs2idx_sorted[bb]]
                fieldname = labels[bb_index][0]
                if fieldname in self.product_fields:
                    if fieldname == field_start and row_index - last_row_index > row_threshold and current_product_cand is not None:
                        products_cand.append(current_product_cand)
                        products_text.append(current_product_text)
                        product_list_boxes.append(current_product_list_boxes)
                        current_product_cand = None
                    if current_product_cand is None:
                        if fieldname == field_start:
                            last_row_index = row_index
                            current_product_cand = {}
                            current_product_text = {}
                            current_product_list_boxes = {}
                            for field in self.product_fields:
                                current_product_cand[field] = []
                                current_product_text[field] = []
                                current_product_list_boxes[field] = []
                    is_add = False
                    if current_product_cand is not None:
                        is_add = True
                        current_product_cand[fieldname].append(bb2cand[bb])
                        current_product_text[fieldname].append(bb2text[bb])
                        current_product_list_boxes[fieldname].append(bb2list_boxes[bb])
                        if fieldname == field_start:
                            last_row_index = row_index
                        if fieldname == field_end:
                            products_cand.append(current_product_cand)
                            products_text.append(current_product_text)
                            product_list_boxes.append(current_product_list_boxes)
                            current_product_cand = None
                    if not is_add and fieldname in field_spec and len(products_cand) != 0:
                        products_cand[-1][fieldname].append(bb2cand[bb])
                        products_text[-1][fieldname].append(bb2text[bb])
                        product_list_boxes[-1][fieldname].append(bb2list_boxes[bb])
                bb_index += 1
        if current_product_cand is not None:
            products_cand.append(current_product_cand)
            products_text.append(current_product_text)
            product_list_boxes.append(current_product_list_boxes)
        return products_cand, products_text, product_list_boxes


    def get_raw_product_type2(self, field_start, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels):
        """
        start and end by same field
        """
        products_cand = []
        products_text = []
        product_list_boxes = []
        current_product_cand = None
        bb_index = 0
        for rbb in rbbs:
            for bb in rbb:
                # fieldname = labels[bbs2idx_sorted[bb]]
                fieldname = labels[bb_index][0]
                if fieldname in self.product_fields:
                    if fieldname == field_start:
                        if current_product_cand is not None:
                            products_cand.append(current_product_cand)
                            products_text.append(current_product_text)
                            product_list_boxes.append(current_product_list_boxes)
                        current_product_cand = {}
                        current_product_text = {}
                        current_product_list_boxes = {}
                        for field in self.product_fields:
                            current_product_cand[field] = []
                            current_product_text[field] = []
                            current_product_list_boxes[field] = []
                    if current_product_cand is not None:

                        current_product_cand[fieldname].append(bb2cand[bb])
                        current_product_text[fieldname].append(bb2text[bb])
                        current_product_list_boxes[fieldname].append(bb2list_boxes[bb])
                bb_index += 1
        if current_product_cand is not None:
            products_cand.append(current_product_cand)
            products_text.append(current_product_text)
            product_list_boxes.append(current_product_list_boxes)
        return products_cand, products_text, product_list_boxes
    


    def get_raw_result(self, receipt_type, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels):
        # get general fields
        raw_result = {}
        raw_text = {}
        raw_list_box = {}
        for field in self.general_fields:
            raw_result[field] = []
            raw_text[field] = []
            raw_list_box[field] = []

        sorted_bbs = [bb for row in rbbs for bb in row]
        for index, (bb, (fieldname, prob)) in enumerate(zip(sorted_bbs, labels)):
            if fieldname in self.general_fields:
                raw_result[fieldname].append(bb2cand[bb])
                raw_text[fieldname].append(bb2text[bb])
                raw_list_box[fieldname].append(bb2list_boxes[bb])
    
        # for rbb in rbbs:
        #     for bb in rbb:
        #         fieldname = labels[bbs2idx_sorted[bb]]
        #         if fieldname in self.general_fields:
        #             raw_result[fieldname].append(bb2cand[bb])
        #             raw_text[fieldname].append(bb2text[bb])
        #             raw_list_box[fieldname].append(bb2list_boxes[bb])
    
        # # get products
        if receipt_type in ['gs25',  'new_gs25',  'emart']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_money', ['product_quantity', 'product_unit_price'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['go', 'topmarket', 'new_bigc',  'newbigc_go_top']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_money', ['product_discount_money'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['coopmart']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type2('product_id', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['vinmart', 'vinmartplus', 'winlife', 'winmart_combined']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_money', ['product_discount_money'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)

        else:
            raise ValueError('Unknown receipt type: {}'.format(receipt_type))
            

        return raw_result, raw_text, raw_list_box
        

    def predict(self, request_id, inp, out, metadata):
        inp_data = inp.get_data()
        inp_data['list_raw_result'] = []
        inp_data['list_raw_text'] = []
        inp_data['list_raw_list_box'] = []
        inp_data['list_box_labels'] = []
        inp_data['list_bbs2idx_sorted'] = []
        inp_data['list_bb2text'] = []
        
        for i in range(len(inp_data['list_bbs'])):
            if len(inp_data['list_bbs'][i]) > 1:
                bb2text, bb2cand, bb2list_boxes, rbbs, bbs2idx_sorted, sorted_indices = self.get_sort_data(inp_data['list_bbs'][i], inp_data['list_list_boxes'][i], inp_data['list_raw_words'][i], inp_data['list_raw_cands'][i])
                
                # x_indexes, y_indexes, text_features, edge_index, edge_type = self.get_input(inp_data['rotated_images'][i], bb2text, rbbs, bbs2idx_sorted, sorted_indices)
                # output_dict = self.request_multi([x_indexes, y_indexes, text_features, edge_index, edge_type])
                # output = np.array(output_dict.as_numpy(self.model_config['output_name']))

                sorted_bbs = [bb for row in rbbs for bb in row]
                sorted_bbs_raw = [np.array(bb).reshape(4, 2) for bb in sorted_bbs]
                sorted_texts = [bb2text[bb] for bb in sorted_bbs]
                image = inp_data['rotated_images'][i]
                labels = self.lmv3.predict_page_prob(image, sorted_bbs_raw, sorted_texts)

                # # labels list for all boxes
                # labels = [self.label_list[i] for i in np.argmax(output, axis=1)]

                raw_result, raw_text, raw_list_box = self.get_raw_result(inp_data['mart_type'], bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
                # pdb.set_trace()
                
                inp_data['list_raw_result'].append(raw_result)
                inp_data['list_raw_text'].append(raw_text)
                inp_data['list_raw_list_box'].append(raw_list_box)
                inp_data['list_box_labels'].append(labels)
                inp_data['list_bbs2idx_sorted'].append(bbs2idx_sorted)
                inp_data['list_bb2text'].append(bb2text)
        
        # combine result
        inp_data['raw_result'] = {}
        inp_data['raw_text'] = {}
        inp_data['raw_list_box'] = {}
        for i in range(len(inp_data['list_raw_result'])):
            for key in inp_data['list_raw_result'][i].keys():
                if key not in inp_data['raw_result'].keys():
                    inp_data['raw_result'][key] = inp_data['list_raw_result'][i][key]
                    inp_data['raw_text'][key] = inp_data['list_raw_text'][i][key]
                    inp_data['raw_list_box'][key] = inp_data['list_raw_list_box'][i][key]
                elif key == 'products' or len(inp_data['raw_result'][key]) == 0:
                    inp_data['raw_result'][key] += inp_data['list_raw_result'][i][key]
                    inp_data['raw_text'][key] += inp_data['list_raw_text'][i][key]
                    inp_data['raw_list_box'][key] += inp_data['list_raw_list_box'][i][key]
                    
        # # special pp for go, bigc, top
        # if inp_data['mart_type'] in ['go', 'new_bigc', 'old_bigc', 'topmarket'] and 'mart_name' in inp_data['raw_text'].keys():
        #     if inp_data['mart_type'] != 'go' and 'go!' in ' '.join(inp_data['raw_text']['mart_name']).lower():
        #         inp_data['mart_type'] == 'go'
        #     elif inp_data['mart_type'] not in ['new_bigc', 'old_bigc'] and 'bigc' in ' '.join(inp_data['raw_text']['mart_name']).lower():
        #         inp_data['mart_type'] == 'new_bigc'
        #     elif inp_data['mart_type'] != 'topmarket' and re.search('^top |top market|tops market', ' '.join(inp_data['raw_text']['mart_name']).lower()) is not None:
        #         inp_data['mart_type'] == 'topmarket'
        
        out.set_data(inp_data)
        return out, metadata