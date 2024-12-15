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


class BaseInformationExtractor(BaseModule):
    def __init__(self, common_config, model_config, word_encoder, label_list, use_emb=True, emb_range=640):
        super(BaseInformationExtractor, self).__init__(common_config, model_config)
        self.word_encoder = word_encoder
        self.label_list = label_list
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
        self.use_emb = use_emb
        self.emb_range = emb_range

    
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

    
    def get_input(self, image, bb2text, rbbs, bbs2idx_sorted, sorted_indices):
        img_h, img_w, _ = image.shape
        # get node features
        x_indexes = [] # list of all x_indexes of all nodes in graph (each node has an x_index)
        y_indexes = [] # list of all y_indexes of all nodes in graph (each node has an y_index)
        text_features = [] # list of all features of all nodes in graph (each node has a feature)
        
        edges = []
        for row_idx, rbb in enumerate(rbbs):
            for bb_idx_in_row, bb in enumerate(rbb):  # duyet qua tung bb (tung node)
                # ----------------- process text feature -----------------
                text = bb2text[bb]
                if self.word_encoder.lang != 'vi':
                    text = unidecode.unidecode(text)  # nếu hóa đơn ko dấu thì bpemb để tiếng việt hay tiếng anh ?
                bb_text_feature = get_manual_text_feature(text) + list(np.sum(self.word_encoder.embed(text), axis=0))
                text_features.append(bb_text_feature)

                # ----------------- process geometry feature -----------------
                xmin, ymin, xmax, ymax = get_bb_from_poly(bb, img_w, img_h)
                if self.use_emb: 
                    # rescale coord at width=self.emb_range
                    x_index = [int(xmin * self.emb_range / img_w), int(xmax * self.emb_range / img_w), int((xmax - xmin) * self.emb_range / img_w)]
                    y_index = [int(ymin * self.emb_range / img_h), int(ymax * self.emb_range / img_h), int((ymax - ymin) * self.emb_range / img_h)]
                else:
                    # normalize in rnage(0, 1)
                    x_index = [float(xmin * 1.0 / img_w), float(xmax * 1.0 / img_w), float((xmax - xmin) * 1.0 / img_w)]
                    y_index = [float(ymin * 1.0 / img_h), float(ymax * 1.0 / img_h), float((ymax - ymin) * 1.0 / img_h)]
                x_indexes.append(x_index)
                y_indexes.append(y_index)
                
                # ------------------------ build graph ----------------------
                # find right node
                right_node = rbb[bb_idx_in_row+1] if bb_idx_in_row < len(rbb) - 1 else None
                if right_node:
                    edges.append([bbs2idx_sorted[bb], bbs2idx_sorted[right_node], 1])
                    edges.append([bbs2idx_sorted[right_node], bbs2idx_sorted[bb], 2])
                
                # find left node
                left_node = rbb[bb_idx_in_row-1] if bb_idx_in_row > 0 else None
                if left_node:
                    edges.append([bbs2idx_sorted[bb], bbs2idx_sorted[left_node], 2])
                    edges.append([bbs2idx_sorted[left_node], bbs2idx_sorted[bb], 1])
                
                # find above node
                max_x_overlap = -1e9
                above_node = None
                if row_idx > 0:
                    for prev_bb in rbbs[row_idx-1]:
                        xmax_prev_bb = max(prev_bb[2], prev_bb[4])
                        xmin_prev_bb = min(prev_bb[0], prev_bb[6])
                        x_overlap = (xmax_prev_bb - xmin_prev_bb) + (xmax-xmin) - (max(xmax_prev_bb, xmax) - min(xmin_prev_bb, xmin))
                        if x_overlap > max_x_overlap:
                            max_x_overlap = x_overlap
                            above_node = prev_bb
                if above_node:
                    edges.append([bbs2idx_sorted[bb], bbs2idx_sorted[above_node], 4])
                    edges.append([bbs2idx_sorted[above_node], bbs2idx_sorted[bb], 3])
                
                # find below node
                max_x_overlap = -1e9
                below_node = None
                if row_idx < len(rbbs) - 1:
                    for next_bb in rbbs[row_idx+1]:
                        xmax_next_bb = max(next_bb[2], next_bb[4])
                        xmin_next_bb = min(next_bb[0], next_bb[2])
                        x_overlap = (xmax_next_bb - xmin_next_bb) + (xmax-xmin) - (max(xmax_next_bb, xmax) - min(xmin_next_bb, xmin))
                        if x_overlap > max_x_overlap:
                            max_x_overlap = x_overlap
                            below_node = next_bb
                if below_node:
                    edges.append([bbs2idx_sorted[bb], bbs2idx_sorted[below_node], 3])
                    edges.append([bbs2idx_sorted[below_node], bbs2idx_sorted[bb], 4])

        # 1 - right, 2 - left, 3 - down, 4  - up
        # edges = torch.tensor(edges, dtype=torch.int32)
        edges = np.unique(edges, axis=0)   # remove duplicate rows
        edge_index, edge_type = edges[:, :2], edges[:, -1]

        return np.array(x_indexes, dtype='int32'),  np.array(y_indexes, dtype='int32'), np.array(text_features, dtype='float32'), np.transpose(edge_index).astype('int64'), np.array(edge_type, dtype='int32')


    def group_product(self, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels, max_row=None):
        current_product_cand = {}
        current_product_text = {}
        current_product_list_boxes = {}
        for field in self.product_fields:
            current_product_cand[field] = []
            current_product_text[field] = []
            current_product_list_boxes[field] = []
        
        if max_row is not None:
            rbbs = rbbs[:max_row]

        for rbb in rbbs:
            for bb in rbb:
                fieldname = labels[bbs2idx_sorted[bb]]
                if fieldname in self.product_fields:
                    current_product_cand[fieldname].append(bb2cand[bb])
                    current_product_text[fieldname].append(bb2text[bb])
                    current_product_list_boxes[fieldname].append(bb2list_boxes[bb])
        return current_product_cand, current_product_text, current_product_list_boxes


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
        for row_index, rbb in enumerate(rbbs):
            for bb in rbb:
                fieldname = labels[bbs2idx_sorted[bb]]
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
        for rbb in rbbs:
            for bb in rbb:
                fieldname = labels[bbs2idx_sorted[bb]]
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
        if current_product_cand is not None:
            products_cand.append(current_product_cand)
            products_text.append(current_product_text)
            product_list_boxes.append(current_product_list_boxes)
        return products_cand, products_text, product_list_boxes
    

    def get_raw_product_type3(self, field_start, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels, max_row=None):
        """
        start at the row containing the 'field_start' and
        end at the row right before the next 'field_start'
        which is not on the same row with the previous one
        max_row: maximum number of row for a product
        """
        products_cand = []
        products_text = []
        product_list_boxes = []
        start, end = None, None
        for row_index, rbb in enumerate(rbbs):
            for bb in rbb:
                fieldname = labels[bbs2idx_sorted[bb]]
                if fieldname in self.product_fields:
                    if fieldname == field_start:
                        if start is None:
                            start = row_index
                        elif end is None and row_index != start:
                            end = row_index
                        if end is not None:
                            current_product_cand, current_product_text, current_product_list_boxes = self.group_product(bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs[start:end], labels, max_row)
                            products_cand.append(current_product_cand)
                            products_text.append(current_product_text)
                            product_list_boxes.append(current_product_list_boxes)
                            start = end
                            end = None
                        
        current_product_cand, current_product_text, current_product_list_boxes = self.group_product(bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs[start:], labels, max_row)
        products_cand.append(current_product_cand)
        products_text.append(current_product_text)
        product_list_boxes.append(current_product_list_boxes)
        return products_cand, products_text, product_list_boxes

    
    def get_raw_product_type4(self, field_start, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels):
        """
        start and end by same field
        add product_name after reparate all products
        """
        products_cand = []
        products_text = []
        product_list_boxes = []
        product_bbs = []
        current_product_cand = None
        product_name_cands = []
        product_name_texts = []
        product_name_list_boxes = []
        product_name_bbs = []
        for rbb in rbbs:
            product_name_line_cands = []
            product_name_line_texts = []
            product_name_line_list_boxes = []
            product_name_line_bbs = []
            for bb in rbb:
                fieldname = labels[bbs2idx_sorted[bb]]
                if fieldname == 'product_name':
                    product_name_line_cands.append(bb2cand[bb])
                    product_name_line_texts.append(bb2text[bb])
                    product_name_line_list_boxes.append(bb2list_boxes[bb])
                    product_name_line_bbs.append(bb)
                    continue
                if fieldname in self.product_fields:
                    if fieldname == field_start:
                        if current_product_cand is not None:
                            products_cand.append(current_product_cand)
                            products_text.append(current_product_text)
                            product_list_boxes.append(current_product_list_boxes)
                            product_bbs.append(current_product_bb)
                        current_product_cand = {}
                        current_product_text = {}
                        current_product_list_boxes = {}
                        current_product_bb = {}
                        for field in self.product_fields:
                            current_product_cand[field] = []
                            current_product_text[field] = []
                            current_product_list_boxes[field] = []
                            current_product_bb[field] = []
                    if current_product_cand is not None:
                        current_product_cand[fieldname].append(bb2cand[bb])
                        current_product_text[fieldname].append(bb2text[bb])
                        current_product_list_boxes[fieldname].append(bb2list_boxes[bb])
                        current_product_bb[fieldname].append(bb)
            if len(product_name_line_cands) != 0:
                product_name_cands.append(product_name_line_cands)
                product_name_texts.append(product_name_line_texts)
                product_name_list_boxes.append(product_name_line_list_boxes)
                product_name_bbs.append(product_name_line_bbs)
        if current_product_cand is not None:
            products_cand.append(current_product_cand)
            products_text.append(current_product_text)
            product_list_boxes.append(current_product_list_boxes)
            product_bbs.append(current_product_bb)
        # add product name
        i = 0
        cnt_line = 0
        cnt_product = 0
        while i < len(product_name_bbs) and cnt_product < len(product_bbs):
            if cnt_product == len(product_bbs) - 1:
                for j in range(i, len(product_name_bbs)):
                    products_cand[cnt_product]['product_name'] += product_name_cands[j]
                    products_text[cnt_product]['product_name'] += product_name_texts[j]
                    product_list_boxes[cnt_product]['product_name'] += product_name_list_boxes[j]
                break
            # bb of product_name_bbs[i][-1] and product_bbs[cnt_product]['product_quantity']
            for key in ['product_quantity', 'product_unit_price', 'product_total_money']:
                for j in range(len(product_bbs[cnt_product][key])):
                    start_product_box = product_bbs[cnt_product][key][j]
                    break
            x1, y1, x2, y2, x3, y3, x4, y4 = product_name_bbs[i][-1]
            ymin_n = min(y1, y2, y3, y4)
            ymax_n = max(y1, y2, y3, y4)
            x1, y1, x2, y2, x3, y3, x4, y4 = start_product_box
            ymin_p = min(y1, y2, y3, y4)
            ymax_p = max(y1, y2, y3, y4)
            # check overlap product_name_bbs[i][-1] vs product_bbs[cnt_product]['product_quantity']
            overlap = ((ymax_n - ymin_n) + (ymax_p - ymin_p) - (max(ymax_p, ymax_n) - min(ymin_p, ymin_n))) / (max(ymax_p, ymax_n) - min(ymin_p, ymin_n))
            if overlap > 0.6:
                for j in range(i - cnt_line, min(i + cnt_line + 1, len(product_name_cands)-1)):
                    products_cand[cnt_product]['product_name'] += product_name_cands[j]
                    products_text[cnt_product]['product_name'] += product_name_texts[j]
                    product_list_boxes[cnt_product]['product_name'] += product_name_list_boxes[j]
                i = i + cnt_line + 1
                cnt_product += 1
                cnt_line = 0
                continue
            # check if product_name_bbs[i][-1] under product_bbs[cnt_product]['product_quantity']
            if ymax_n > ymax_p:
                for j in range(i - cnt_line, min(i + cnt_line, len(product_name_cands)-1)):
                    products_cand[cnt_product]['product_name'] += product_name_cands[j]
                    products_text[cnt_product]['product_name'] += product_name_texts[j]
                    product_list_boxes[cnt_product]['product_name'] += product_name_list_boxes[j]
                i = i + cnt_line
                cnt_product += 1
                cnt_line = 0
                continue
            cnt_line += 1
            i += 1
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
        for rbb in rbbs:
            for bb in rbb:
                fieldname = labels[bbs2idx_sorted[bb]]
                if fieldname in self.general_fields:
                    raw_result[fieldname].append(bb2cand[bb])
                    raw_text[fieldname].append(bb2text[bb])
                    raw_list_box[fieldname].append(bb2list_boxes[bb])
        # get products
        if receipt_type in ['aeon', 'bhx', 'dmx', 'gs25', 'hc', 'heineken', 'lamthao', 'nova', 'nuty', 'satra', 'tgs', 'tgsf', 'new_gs25', 'ministop', 'emart', 'circlek', 'lotteria', 'bhd', 'cheers', 'bhx_2024', 'kingfood', 'tiemlaunho', 'sayaka']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_money', ['product_quantity', 'product_unit_price'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['go', 'topmarket', 'new_bigc', 'family_mart']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_money', ['product_discount_money'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['lotte']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_money', ['product_discount_money', 'product_total_money'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['711']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type2('product_quantity', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['brg', 'coopmart', 'fujimart', 'guardian', 'mega', 'coopfood', 'bsmart']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type2('product_id', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['aeoncitimart', 'vinmart', 'vinmartplus', 'winlife']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_money', ['product_discount_money'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['nguyenkim']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_quantity', ['product_unit_price', 'product_total_money'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['lanchi', 'old_bigc']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_original_money', ['product_original_price', 'product_quantity'], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['thegioisua']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_id', [], 2, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['bitis']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type1('product_name', 'product_total_money', [], 1, bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['pizza_company', 'don_chicken', 'okono', 'galaxy_cinema']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type3('product_quantity', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['kfc']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type3('product_name', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['heineken_2024']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type3('product_total_money', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['pepper_lunch']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type3('product_total_money', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels, max_row=1)
        elif receipt_type in ['lotte_cinema']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type3('product_quantity', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels, max_row=1)
        elif receipt_type in ['sukiya', 'umyoshi']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type3('product_quantity', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels, max_row=2)
        elif receipt_type in ['globalx']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type3('product_quantity', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels, max_row=3)
        elif receipt_type in ['bonchon']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type4('product_quantity', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
        elif receipt_type in ['launuongmai']:
            raw_result['products'], raw_text['products'], raw_list_box['products'] = self.get_raw_product_type4('product_unit_price', bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)

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
                x_indexes, y_indexes, text_features, edge_index, edge_type = self.get_input(inp_data['rotated_images'][i], bb2text, rbbs, bbs2idx_sorted, sorted_indices)
                output_dict = self.request_multi([x_indexes, y_indexes, text_features, edge_index, edge_type])
                output = np.array(output_dict.as_numpy(self.model_config['output_name']))
                labels = [self.label_list[i] for i in np.argmax(output, axis=1)]
                raw_result, raw_text, raw_list_box = self.get_raw_result(inp_data['mart_type'], bb2text, bb2cand, bb2list_boxes, bbs2idx_sorted, rbbs, labels)
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
                    
        # special pp for go, bigc, top
        if inp_data['mart_type'] in ['go', 'new_bigc', 'old_bigc', 'topmarket'] and 'mart_name' in inp_data['raw_text'].keys():
            if inp_data['mart_type'] != 'go' and 'go!' in ' '.join(inp_data['raw_text']['mart_name']).lower():
                inp_data['mart_type'] == 'go'
            elif inp_data['mart_type'] not in ['new_bigc', 'old_bigc'] and 'bigc' in ' '.join(inp_data['raw_text']['mart_name']).lower():
                inp_data['mart_type'] == 'new_bigc'
            elif inp_data['mart_type'] != 'topmarket' and re.search('^top |top market|tops market', ' '.join(inp_data['raw_text']['mart_name']).lower()) is not None:
                inp_data['mart_type'] == 'topmarket'
        # special pp for ushimania yoshinoya
        elif inp_data['mart_type'] in ['umyoshi'] and 'mart_name' in inp_data['raw_text'].keys():
            text = ' '.join(inp_data['raw_text']['mart_name']).lower()
            inp_data['mart_type'] = 'ushimania'
            if 'yoshi' in text:
                inp_data['mart_type'] = 'yoshinoya'
        out.set_data(inp_data)
        return out, metadata