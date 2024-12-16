import os
import re
import pdb
import math
import copy
import numpy as np

from bpemb import BPEmb
from modules.base_module import BaseModule
from utils.utils import total_time


class BaseInformationExtractor(BaseModule):
    def __init__(self, common_config, model_config):
        super(BaseInformationExtractor, self).__init__(common_config, model_config)
        self.word_encoder = BPEmb(lang='vi', vs=5000, dim=100)
        self.use_emb = True
        self.emb_range = 640


    def clip_box(self, xmin, ymin, xmax, ymax, img_w, img_h):
        xmin = np.clip(xmin, 0, img_w)
        ymin = np.clip(ymin, 0, img_h)
        xmax = np.clip(xmax, 0, img_w)
        ymax = np.clip(ymax, 0, img_h)
        return xmin, ymin, xmax, ymax


    def get_bb_from_poly(self, poly):
        x1, y1, x2, y2, x3, y3, x4, y4 = poly    # tl -> tr -> br -> bl
        xmin = min (x1, x4)
        xmax = max (x2, x3)
        ymin = min (y1, y2)
        ymax = max (y3, y4)
        return xmin, ymin, xmax, ymax


    def get_manual_text_feature(self, text: str):
        feature = []
    
        # có phải ngày tháng không
        feature.append(int(re.search('(\d{1,2})\/(\d{1,2})\/(\d{4})', text) != None))
    
        # co phai gio khong
        # feature.append(int(re.search('(\d{1,2}):(\d{1,2})', text) != None))
            
        # có phải ma hang hoa khong
        # feature.append(int(re.search('^\d+$', text) != None and len(text) > 5))
    
        # có phải tiền dương không
        # feature.append(int(re.search('^\d{1,3}(\,\d{3})*(\,00)+$', text.replace('.', ',')) != None or re.search('^\d{1,3}(\,\d{3})+$', text.replace('.', ',')) != None))
        
        # co phai tien am khong
        # feature.append(int(text.startswith('-') and re.search('^[\d(\,)]+$', text[1:].replace('.', ',')) != None and len(text) >= 3))
    
        # có phải uppercase
        feature.append(int(text.isupper()))
    
        # có phải title
        feature.append(int(text.istitle()))
    
        # có phải lowercase
        feature.append(int(text.islower()))
        
        # có phải chỉ chứa chữ in hoa và số
        feature.append(int(re.search('^[A-Z0-9]+$', text) != None))
    
        # chỉ có số
        feature.append(int(re.search('^\d+$', text) != None))
    
        # chỉ có chữ cái
        feature.append(int(re.search('^[a-zA-Z]+$', text) != None))
    
        # chi co chu hoac so
        feature.append(int(re.search('^[a-zA-Z0-9]+$', text) != None))
    
        # chỉ có số và dấu
        feature.append(int(re.search('^[\d|\-|\'|,|\(|\)|.|\/|&|:|+|~|*|\||_|>|@|%]+$', text) != None))
    
        # chỉ có chữ và dấu
        feature.append(int(re.search('^[a-zA-Z|\-|\'|,|\(|\)|.|\/|&|:|+|~|*|\||_|>|@|%]+$', text) != None))
    
        return feature

    
    def get_input(self, image, bb2text, rbbs, bbs2idx_sorted, sorted_indices):
        img_h, img_w, _ = image.shape
    
        # get node features
        x_indexes = [] # list of all x_indexes of all nodes in graph (each node has an x_index)
        y_indexes = [] # list of all y_indexes of all nodes in graph (each node has an y_index)
        text_features = [] # list of all features of all nodes in graph (each node has a feature)
    
        nodes, edges, labels  = [], [], []
        for row_idx, rbb in enumerate(rbbs):
            for bb_idx_in_row, bb in enumerate(rbb):  # duyet qua tung bb (tung node)
                # ----------------- process text feature -----------------
                text = bb2text[bb]
                if self.word_encoder.lang != 'vi':
                    text = unidecode.unidecode(text)  # nếu hóa đơn ko dấu thì bpemb để tiếng việt hay tiếng anh ?
                bb_text_feature = self.get_manual_text_feature(text) + list(np.sum(self.word_encoder.embed(text), axis=0))  # need fix
                text_features.append(bb_text_feature)
    
                # ----------------- process geometry feature -----------------
                xmin, ymin, xmax, ymax = self.get_bb_from_poly(bb)
                xmin, ymin, xmax, ymax = self.clip_box(xmin, ymin, xmax, ymax, img_w, img_h)
    
                if self.use_emb: 
                    # rescale coord at width=emb_range
                    x_index = [int(xmin * 1. / img_w * self.emb_range), int(xmax * 1. / img_w * self.emb_range), int((xmax - xmin) * 1. / img_w * self.emb_range)]
                    y_index = [int(ymin * 1. / img_h * self.emb_range), int(ymax * 1. / img_h * self.emb_range), int((ymax - ymin) * 1. / img_h * self.emb_range)]
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
                    edges.append([bbs2idx_sorted[bb], bbs2idx_sorted[right_node], 0])
                    edges.append([bbs2idx_sorted[right_node], bbs2idx_sorted[bb], 1])
                
                # find left node
                left_node = rbb[bb_idx_in_row-1] if bb_idx_in_row > 0 else None
                if left_node:
                    edges.append([bbs2idx_sorted[bb], bbs2idx_sorted[left_node], 1])
                    edges.append([bbs2idx_sorted[left_node], bbs2idx_sorted[bb], 0])
                
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
                    edges.append([bbs2idx_sorted[bb], bbs2idx_sorted[above_node], 3])
                    edges.append([bbs2idx_sorted[above_node], bbs2idx_sorted[bb], 2])
                
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
                    edges.append([bbs2idx_sorted[bb], bbs2idx_sorted[below_node], 2])
                    edges.append([bbs2idx_sorted[below_node], bbs2idx_sorted[bb], 3])
    
        # 1 - right, 2 - left, 3 - down, 4  - up
        edges = np.unique(edges, axis=0)
        edge_index, edge_type = edges[:, :2], edges[:, -1]
        return np.array(x_indexes, dtype=np.int32), np.array(y_indexes, dtype=np.int32), np.array(text_features, dtype=np.float32), np.transpose(edge_index).astype(np.int64), np.array(edge_type, dtype=np.int32)    


    def get_sort_data(self, text_boxes, raw_words, raw_cands):
        bbs, texts, cands = [], [], []
        for box, text, cand in zip(text_boxes, raw_words, raw_cands):
            x1, y1 = box[0]  # tl
            x2, y2 = box[1]  # tr
            x3, y3 = box[2]  # br
            x4, y4 = box[3]  # bl
            bb = tuple(int(i) for i in (x1,y1,x2,y2,x3,y3,x4,y4))
            bbs.append(bb)
            texts.append(text)
            cands.append(cand)
    
        bb2text = dict(zip(bbs, texts))
        bb2cand = dict(zip(bbs, cands))
        bb2idx_original = {x: idx for idx, x in enumerate(bbs)}   # theo thu tu truyen vao trong data['shapes']
        rbbs = self.row_bbs(copy.deepcopy(bbs))
        sorted_bbs = [bb for row in rbbs for bb in row]  # theo thu tu tu trai sang phai, tu tren xuong duoi
        bb2idx_sorted = {tuple(x): idx for idx, x in enumerate(sorted_bbs)}   # theo thu tu tu trai sang phai, tu tren xuong duoi
        sorted_indices = [bb2idx_sorted[bb] for bb in bb2idx_original.keys()]
    
        return bb2text, bb2cand, rbbs, bb2idx_sorted, sorted_indices


    def max_left(self, bb):
        return min(bb[0], bb[2], bb[4], bb[6])
   

    def max_right(self, bb):
        return max(bb[0], bb[2], bb[4], bb[6])
   

    def row_bbs(self, bbs):
        bbs.sort(key=lambda x: self.max_left(x))
        clusters, y_min = [], []
        for tgt_node in bbs:
            if len (clusters) == 0:
                clusters.append([tgt_node])
                y_min.append(tgt_node[1])
                continue
            matched = None
            tgt_7_1 = tgt_node[7] - tgt_node[1]
            min_tgt_0_6 = min(tgt_node[0], tgt_node[6])
            max_tgt_2_4 = max(tgt_node[2], tgt_node[4])
            max_left_tgt = self.max_left(tgt_node)
            for idx, clt in enumerate(clusters):
                src_node = clt[-1]
                src_5_3 = src_node[5] - src_node[3]
                max_src_2_4 = max(src_node[2], src_node[4])
                min_src_0_6 = min(src_node[0], src_node[6])
                overlap_y = (src_5_3 + tgt_7_1) - (max(src_node[5], tgt_node[7]) - min(src_node[3], tgt_node[1]))
                overlap_x = (max_src_2_4 - min_src_0_6) + (max_tgt_2_4 - min_tgt_0_6) - (max(max_src_2_4, max_tgt_2_4) - min(min_src_0_6, min_tgt_0_6))
                if overlap_y > 0.5*min(src_5_3, tgt_7_1) and overlap_x < 0.6*min(max_src_2_4 - min_src_0_6, max_tgt_2_4 - min_tgt_0_6):
                    distance = max_left_tgt - self.max_right(src_node)
                    if matched is None or distance < matched[1]:
                        matched = (idx, distance)
            if matched is None:
                clusters.append([tgt_node])
                y_min.append(tgt_node[1])
            else:
                idx = matched[0]
                clusters[idx].append(tgt_node)
        zip_clusters = list(zip(clusters, y_min))
        zip_clusters.sort(key=lambda x: x[1])
        zip_clusters = list(np.array(zip_clusters, dtype=object)[:, 0])
        return zip_clusters
    
    def sort_bbs(self, bbs):
        bb_clusters = self.row_bbs(bbs)
        bbs = []
        for cl in bb_clusters:
            bbs.extend(cl)
        return bbs, bb_clusters
   

    def to_4_points(self, box):
        x1, y1, x2, y2, x3, y3, x4, y4 = box
        xmin = min(x1, x2, x3, x4)
        xmax = max(x1, x2, x3, x4)
        ymin = min(y1, y2, y3, y4)
        ymax = max(y1, y2, y3, y4)
        return [int(xmin), int(ymin), int(xmax), int(ymax)]
    

