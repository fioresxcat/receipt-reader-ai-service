import os
import pdb
import unidecode
import numpy as np
import math
import Levenshtein

from transformers import LayoutXLMTokenizerFast, LayoutLMv3FeatureExtractor, LayoutLMv3Processor
from utils.utils import total_time
from modules.information_extraction.layoutlmv3.utils import sort_bbs, box_normalize
from modules.information_extraction.layoutlmv3.base_information_extraction import InformationExtractor


class LayoutLMv3Predictor(InformationExtractor):
    instance = None
    
    def __init__(self, common_config, model_config, label_list):
        super(LayoutLMv3Predictor, self).__init__(common_config, model_config)
        current_path = os.path.abspath(os.path.dirname(__file__))
        self.processor = LayoutLMv3Processor.from_pretrained(os.path.join(current_path, self.model_config['model_dir']), apply_ocr=False)
        self.processor.tokenizer.only_label_first_subword = False
        self.label_list = label_list
        self.label2id = {label: id for id, label in enumerate(self.label_list)}
        self.id2label = {id: label for id, label in enumerate(self.label_list)}
        self.max_line_distance = 1
        self.max_word_distance = 1
        self.max_distance = 3

        
    @staticmethod
    def get_instance(common_config, model_config):
        if LayoutLMv3Predictor.instance is None:
            LayoutLMv3Predictor.instance = LayoutLMv3Predictor(common_config, model_config)
        return LayoutLMv3Predictor.instance
    
    
    def get_raw_fields(self, bb_clusters, avg_h):
        """
            avg_h: average height of all boxes in the (page) image
        """
        last_info = {}
        raw_ocrs = {}
        raw_cands = {}
        raw_ie_scores = {}
        coordinates = {}
        text_indexes = {}
        for label in self.label_list:
            last_info[label] = [-10, -10, -10] # line, box, real_line
            raw_ocrs[label] = []
            raw_cands[label] = []
            raw_ie_scores[label] = []
            coordinates[label] = []
            text_indexes[label] = []
            
        # điều kiện để tách ra 1 field mới nếu cùng tên là cách ??? text box ??? line
        count_bb = 0
        count_line = 0
        list_all_cands = []
        list_all_texts = []
        list_all_labels = []
        list_all_bbs = []
        list_all_lines = []
        marker_line = -10
        has_confuse_seller = False
        payment_bank_index = -1
        seller_index = -1
        buyer_index = -1
        
        for bb_cluster_index, bb_cluster in enumerate(bb_clusters):  # for each  row
            count_line += 1  # increase the current line
            bbs, _, texts, labels, cands = bb_cluster  # get boxes, texts, and labels data in the row
            if len(texts) < 4:  # if line has less then 4 boxes
                count_line -= 0.5
            for bb, text, (label, ie_score), cand in zip(bbs, texts, labels, cands):  # for each box in row
                count_bb += 1  # count boxes for the whole image
                # append data for the whole image
                list_all_cands.append(cand)
                list_all_texts.append(text)
                list_all_labels.append(label)
                list_all_bbs.append(bb)
                list_all_lines.append(bb_cluster_index)
                
                if label in ['buyer_name', 'seller_name', 'receiver_name', 'seller_address', 'buyer_address', 'receiver_address', 'loading_port', 'discharge_port', 'delivery_time', 'receiver_name', 'receiver_bank_name', 'producer', 'consignor']:  # fields that has only 1 final values
                    # if there is seller at the top and has no marker
                    if label == 'seller_name' and count_line < 10 and count_line - marker_line > 1:
                        has_confuse_seller = True
                        
                    # if the current line IS THE MOST RECENT LINE of this label but current_bb is far from the last_bb of this label -> generate new cands
                    if (count_line - last_info[label][0] == 0) or (count_line - last_info[label][0] == 1 and label == 'receiver_bank_name'):
                        min_w = min(bb[::2])
                        if (count_bb - last_info[label][1] > self.max_word_distance + 1) or (min_w - coordinates[label][-1][2] > self.max_distance*avg_h):
                            raw_ocrs[label].append([])
                            raw_cands[label].append([])
                            raw_ie_scores[label].append([])
                            coordinates[label].append([])
                            text_indexes[label].append([count_bb, count_bb])
                    # eilf the current line is near the most recent line of this label AND current_bb and last_bb is far (in interms of y-axis) AND current_bb index is far from last_bb index -> generate new cands
                    elif count_line - last_info[label][0] <= self.max_line_distance:
                        y11, y12 = min(bb[::2]), max(bb[::2])  # ymin, ymax of current bb
                        y21, y22 = coordinates[label][-1][0], coordinates[label][-1][2]  # ymin, ymax of last_bb of this label
                        if (max(y12, y22) - min(y21, y11)) - ((y12 - y11) + (y22 - y21)) > 10 and (count_bb - last_info[label][1] > self.max_word_distance + 6):
                            raw_ocrs[label].append([])
                            raw_cands[label].append([])
                            raw_ie_scores[label].append([])
                            coordinates[label].append([])
                            text_indexes[label].append([count_bb, count_bb])
                            
                    # elif the current line is far from the most recent line of this label -> generate new cands
                    elif count_line - last_info[label][0] > self.max_line_distance:
                        is_new_cand = True
                        if label in ['seller_address', 'buyer_address', 'receiver_address']:
                            if last_info[label][2] > 0:
                                cur_bbs = bbs
                                last_cluster = bb_clusters[last_info[label][2]]
                                last_bbs = last_cluster[0]
                                cur_line_ymin = np.mean([min(cur_bb[1::2]) for cur_bb in cur_bbs])
                                last_line_ymax = np.mean([max(last_bb[1::2]) for last_bb in last_bbs])
                                cur_line_height = np.mean([max(cur_bb[1::2]) - min(cur_bb[1::2]) for cur_bb in cur_bbs])
                                last_line_height = np.mean([max(last_bb[1::2]) - min(last_bb[1::2]) for last_bb in last_bbs])
                                # if distance from this line to the last line is small -> it is still the same cand, otherwise this is a new cand
                                if abs(cur_line_ymin - last_line_ymax) < (cur_line_height+last_line_height) / 2:
                                    is_new_cand = False
                        if is_new_cand:
                            raw_ocrs[label].append([])
                            raw_cands[label].append([])
                            raw_ie_scores[label].append([])
                            coordinates[label].append([])
                            text_indexes[label].append([count_bb, count_bb])

                    # update seller index if seller has marker -> seller index is the index of last seller with marker
                    if label == 'seller_name' and seller_index == -1 and count_line - marker_line < 2:
                        seller_index = len(raw_ocrs[label]) - 1  # seller_index is the last seller if current line is near marker_line
                    # update buyer index
                    if label == 'buyer_name' and buyer_index == -1 and count_line - marker_line < 2:
                        buyer_index = len(raw_ocrs[label]) - 1  # buyer_index is the last buyer with marker

                elif label == 'payment_term':
                    # if current line is far from the most recent line of payment term -> generate a new cand for payment_term
                    if count_line - last_info[label][0] > self.max_line_distance:
                        raw_ocrs[label].append([])
                        raw_cands[label].append([])
                        raw_ie_scores[label].append([])
                        coordinates[label].append([])
                        text_indexes[label].append([count_bb, count_bb])
                    else:  # if current line is near the most recent line of payment_term
                        if count_bb - last_info[label][1] > 1:  # if current_bb (also payment_term) is far from the last_bb of payment term
                            # if the last_bb of receiver_bank is in range(last_bb_of_payment, current_bb) -> this is bank_in_payment
                            if last_info['receiver_bank_name'][1] > last_info[label][1] and last_info['receiver_bank_name'][1] < count_bb:
                                payment_bank_index = len(raw_ocrs['receiver_bank_name']) - 1
                            # # get all box from last_bb_of_payment to current_bb as payment
                            # for bb_i in range(last_info[label][1], count_bb - 1):
                            #     raw_ocrs[label][-1].append(list_all_texts[bb_i])
                            #     raw_cands[label][-1].append(list_all_cands[bb_i])
                                
                # elif current line is not the most recent line of label | current bb is far from the last bb of label -> generate new cands            
                elif count_line - last_info[label][0] > 0 or count_bb - last_info[label][1] > self.max_word_distance:
                    raw_ocrs[label].append([])
                    raw_cands[label].append([])
                    raw_ie_scores[label].append([])
                    coordinates[label].append([])
                    text_indexes[label].append([count_bb, count_bb])
                
                else:
                    min_w = min(bb[::2])
                    if min_w - coordinates[label][-1][2] > self.max_distance*avg_h:
                        raw_ocrs[label].append([])
                        raw_cands[label].append([])
                        raw_ie_scores[label].append([])
                        coordinates[label].append([])
                        text_indexes[label].append([count_bb, count_bb])

                # update marker line index
                if label == 'marker_company_name':
                    marker_line = count_line
                coord = self.to_4_points(bb)

                last_info[label] = [count_line, count_bb, bb_cluster_index] # line, box, real_line
                append_idx = -1
                if label in ['buyer_address', 'buyer_name']:
                    if len(raw_ocrs[label][-1]) == 0 or len(raw_ocrs[label]) < 2:
                        pass
                    else:
                        last_coord = coordinates[label][-1]
                        second_last_coord = coordinates[label][-2]
                        # check if the two is horizontal
                        overlap_y = max(0, min(last_coord[3], second_last_coord[3]) - max(last_coord[1], second_last_coord[1]))
                        ratio = max(overlap_y/(last_coord[3]-last_coord[1]), overlap_y/(second_last_coord[3]-second_last_coord[1]))
                        # pdb.set_trace()
                        if ratio > 0.2:  # is horizontal
                            ls_overlap_x = []
                            for cand_coord in [second_last_coord, last_coord]:
                                overlap_x = min(max(bb[::2]), cand_coord[2]) - max(min(bb[::2]), cand_coord[0])
                                ls_overlap_x.append(overlap_x)
                            max_idx = ls_overlap_x.index(max(ls_overlap_x))
                            append_idx = -2 if max_idx == 0 else -1

                # append box data to cand
                raw_ocrs[label][append_idx].append(text)
                raw_cands[label][append_idx].append(cand)
                raw_ie_scores[label][append_idx].append(ie_score)
                text_indexes[label][append_idx][1] = count_bb
                
                # update the coordinates for the cand
                if len(coordinates[label][append_idx]) == 0:
                    coordinates[label][append_idx] = coord
                else:
                    c_xmin, c_ymin, c_xmax, c_ymax = coordinates[label][append_idx]
                    new_coord = [min(c_xmin, coord[0]), min(c_ymin, coord[1]), max(c_xmax, coord[2]), max(c_ymax, coord[3])]
                    coordinates[label][append_idx] = new_coord
                    
        # for field in ['text', 'marker_company_name', 'marker_receiver_bank_name', 'marker_receiver_name', 'marker_receiver_account_number']:
        for field in ['text']:
            raw_ocrs.pop(field)
            raw_cands.pop(field)
            raw_ie_scores.pop(field)
            coordinates.pop(field)
            text_indexes.pop(field)
        # remove confuse seller buyer
        if has_confuse_seller and len(raw_ocrs['seller_name']) > 1 and seller_index == -1:  # seller_index=-1 mean no seller has marker
            raw_ocrs['seller_name'] = raw_ocrs['seller_name'][1:]
            raw_cands['seller_name'] = raw_cands['seller_name'][1:]
            raw_ie_scores['seller_name'] = raw_ie_scores['seller_name'][1:]
            coordinates['seller_name'] = coordinates['seller_name'][1:]
            text_indexes['seller_name'] = text_indexes['seller_name'][1:]
        # choose seller and buyer has marker
        if seller_index != -1:  # has seller with marker
            raw_ocrs['seller_name'] = raw_ocrs['seller_name'][seller_index:]
            raw_cands['seller_name'] = raw_cands['seller_name'][seller_index:]
            raw_ie_scores['seller_name'] = raw_ie_scores['seller_name'][seller_index:]
            coordinates['seller_name'] = coordinates['seller_name'][seller_index:]
            text_indexes['seller_name'] = text_indexes['seller_name'][seller_index:]
            # nếu seller có marker nằm dưới 1 seller khác, lấy seller_address nằm dưới seller có marker
            name_coord = coordinates['seller_name'][0]
            best_index = 0
            if seller_index > 0:
                for index in range(len(coordinates['seller_address'])):
                    address_coord = coordinates['seller_address'][index]
                    if max(address_coord[1::2]) > min(name_coord[1::2]):
                        best_index = index
                        break
            raw_ocrs['seller_address'] = raw_ocrs['seller_address'][best_index:]
            raw_cands['seller_address'] = raw_cands['seller_address'][best_index:]
            raw_ie_scores['seller_address'] = raw_ie_scores['seller_address'][best_index:]
            coordinates['seller_address'] = coordinates['seller_address'][best_index:]
            text_indexes['seller_address'] = text_indexes['seller_address'][best_index:]

        if buyer_index != -1:
            raw_ocrs['buyer_name'] = raw_ocrs['buyer_name'][buyer_index:]
            raw_cands['buyer_name'] = raw_cands['buyer_name'][buyer_index:]
            raw_ie_scores['buyer_name'] = raw_ie_scores['buyer_name'][buyer_index:]
            coordinates['buyer_name'] = coordinates['buyer_name'][buyer_index:]
            text_indexes['buyer_name'] = text_indexes['buyer_name'][buyer_index:]
            # nếu buyer có marker nằm dưới 1 buyer khác, lấy buyer_address nằm dưới buyer có marker
            name_coord = coordinates['buyer_name'][0]
            best_index = 0
            if buyer_index > 0:
                for index in range(len(coordinates['buyer_address'])):
                    address_coord = coordinates['buyer_address'][index]
                    if max(address_coord[1::2]) > min(name_coord[1::2]):
                        best_index = index
                        break
            raw_ocrs['buyer_address'] = raw_ocrs['buyer_address'][best_index:]
            raw_cands['buyer_address'] = raw_cands['buyer_address'][best_index:]
            raw_ie_scores['buyer_address'] = raw_ie_scores['buyer_address'][best_index:]
            coordinates['buyer_address'] = coordinates['buyer_address'][best_index:]
            text_indexes['buyer_address'] = text_indexes['buyer_address'][best_index:]
            
        # remove payment term bank if has 2 receiver bank name
        if len(raw_ocrs['receiver_bank_name']) > 1 and payment_bank_index != -1:
            raw_ocrs['receiver_bank_name'].pop(payment_bank_index)
            raw_cands['receiver_bank_name'].pop(payment_bank_index)
            raw_ie_scores['receiver_bank_name'].pop(payment_bank_index)
            coordinates['receiver_bank_name'].pop(payment_bank_index)
            text_indexes['receiver_bank_name'].pop(payment_bank_index)
            
        # swap buyer seller of purchase order
        if len(raw_ocrs['seller_name']) > 0 and len(raw_ocrs['buyer_name']) > 0:
            need_swap = True
            seller_line = list_all_lines[text_indexes['seller_name'][0][1]]  # get index of seller line
            for i in range(len(list_all_labels)):  # list_all_labels is list of all labels for all boxes in the page
                if seller_line - list_all_lines[i] <= 1:
                    if list_all_labels[i] == 'marker_company_name' and any([el in list_all_texts[i].lower() for el in ['sell', 'suppl', 'export']]):  # if is arriving at a marker_seller box
                        if i < text_indexes['seller_name'][0][0] and  i > text_indexes['seller_name'][0][0] - 5:  # if seller has marker -> exit for loop immidiately
                            need_swap = False
                            break
                        # check marker có nằm ngay bên trên seller_name hay không? -> if yes -> exit for loop
                        y11, y12 = min(list_all_bbs[i][::2]), max(list_all_bbs[i][::2])
                        y21, y22 = coordinates['seller_name'][0][::2]
                        overlap = (y12 - y11) + (y22 - y21) - (max(y22, y12) - min(y11, y21))
                        if overlap > 0:
                            need_swap = False
                            break
            if need_swap:
                # check if title == purchase order
                max_distance = 0.
                for i in range(1, text_indexes['buyer_name'][0][0]):
                    for pattern in ['purchaseorder', 'purchasingorder']:
                        dis1 = 1 - (Levenshtein.distance(unidecode.unidecode(list_all_texts[i-1].lower()), pattern) / len(pattern))
                        dis2 = 1 - (Levenshtein.distance(unidecode.unidecode(''.join(list_all_texts[i-1:i+1]).lower()), pattern) / len(pattern))
                        max_distance = max(max_distance, dis1, dis2)
                # swap buyer and seller
                if max_distance > 0.9:
                    raw_ocrs['seller_name'][0], raw_ocrs['buyer_name'][0] = raw_ocrs['buyer_name'][0], raw_ocrs['seller_name'][0]
                    raw_cands['seller_name'][0], raw_cands['buyer_name'][0] = raw_cands['buyer_name'][0], raw_cands['seller_name'][0]
                    raw_ie_scores['seller_name'][0], raw_ie_scores['buyer_name'][0] = raw_ie_scores['buyer_name'][0], raw_ie_scores['seller_name'][0]
                    coordinates['seller_name'][0], coordinates['buyer_name'][0] = coordinates['buyer_name'][0], coordinates['seller_name'][0]
                    text_indexes['seller_name'][0], text_indexes['buyer_name'][0] = text_indexes['buyer_name'][0], text_indexes['seller_name'][0]
                    if len(raw_ocrs['seller_address']) != 0 and len(raw_ocrs['buyer_address']) != 0:
                        raw_ocrs['seller_address'][0], raw_ocrs['buyer_address'][0] = raw_ocrs['buyer_address'][0], raw_ocrs['seller_address'][0]
                        raw_cands['seller_address'][0], raw_cands['buyer_address'][0] = raw_cands['buyer_address'][0], raw_cands['seller_address'][0]
                        raw_ie_scores['seller_address'][0], raw_ie_scores['buyer_address'][0] = raw_ie_scores['buyer_address'][0], raw_ie_scores['seller_address'][0]
                        coordinates['seller_address'][0], coordinates['buyer_address'][0] = coordinates['buyer_address'][0], coordinates['seller_address'][0]
                        text_indexes['seller_address'][0], text_indexes['buyer_address'][0] = text_indexes['buyer_address'][0], text_indexes['seller_address'][0]
        # pdb.set_trace()
        return raw_ocrs, raw_cands, raw_ie_scores, coordinates
    
    
    @total_time
    def predict(self, request_id, inp, out, metadata):
        inp_data = inp.get_data()
        
        list_raw_ocrs = []
        list_raw_cands = []
        list_raw_ie_scores = []
        list_coordinates = []
        list_bb_clusters = []
        for page_index in range(len(inp_data['pages'])):
            # normalize box
            inp_data['pages'][page_index]['bbs'], inp_data['pages'][page_index]['raw_words'], inp_data['pages'][page_index]['bbs_raw'], inp_data['pages'][page_index]['raw_cands'], avg_h = box_normalize(inp_data['pages'][page_index]['bbs'], inp_data['pages'][page_index]['raw_words'], inp_data['pages'][page_index]['bbs_raw'], inp_data['pages'][page_index]['raw_cands'])
            # sort bbs
            # this part will update the inp_data['pages'][page_index] boxes and texts data in the sorted order
            bb_clusters = sort_bbs(inp_data['pages'][page_index]['bbs'], inp_data['pages'][page_index]['raw_words'], inp_data['pages'][page_index]['bbs_raw'], inp_data['pages'][page_index]['raw_cands'])
            new_bbs = []
            new_raw_words = []
            new_bbs_raw = []
            new_raw_cands = []
            for bb_cluster in bb_clusters: # for each row (bb_cluster = row)
                bbs, _, raw_words, bb_raws, raw_cands = bb_cluster
                new_bbs += bbs
                new_raw_words += raw_words
                new_bbs_raw += bb_raws
                new_raw_cands += raw_cands
            inp_data['pages'][page_index]['bbs'] = new_bbs
            inp_data['pages'][page_index]['raw_words'] = new_raw_words
            inp_data['pages'][page_index]['bbs_raw'] = new_bbs_raw
            inp_data['pages'][page_index]['raw_cands'] = new_raw_cands
            # predict labels
            image = inp_data['images'][page_index]
            # because bbs_raw and raw_words is sorted, there is no need to sort in the predict_page_prob method
            labels = self.predict_page_prob(image, inp_data['pages'][page_index]['bbs_raw'], inp_data['pages'][page_index]['raw_words'])
            # re-sort with the predicted labels
            bb_clusters = sort_bbs(inp_data['pages'][page_index]['bbs'], inp_data['pages'][page_index]['raw_words'], labels, inp_data['pages'][page_index]['raw_cands'])
            metadata = self.add_metadata(metadata, 1, 1)
            # generate candidates from boxes and predicted labels for each page
            raw_ocrs, raw_cands, raw_ie_scores, coordinates = self.get_raw_fields(bb_clusters, avg_h)
            # append each page's result to result of the whole document
            list_raw_ocrs.append(raw_ocrs)
            list_raw_cands.append(raw_cands)
            list_raw_ie_scores.append(raw_ie_scores)
            list_coordinates.append(coordinates)
            list_bb_clusters.append(bb_clusters)
        # the generated candidates is in document-scope, so they'll be a direct key of inp_data
        # the bbs, raw_words, raw_cands of each page above is page-cope, so they'll live under the 'pages' field of inp_data
        inp_data['raw_ocrs'] = list_raw_ocrs
        inp_data['raw_cands'] = list_raw_cands
        inp_data['raw_ie_scores'] = list_raw_ie_scores
        inp_data['coordinates'] = list_coordinates
        inp_data['bb_clusters'] = list_bb_clusters
        inp_data['charset_list'] = inp_data['charset_list']
        out.set_data(inp_data)
        return out, metadata
            
