import re
import pdb
import cv2
import math
import numpy as np

from utils.utils import total_time
from modules.base_module import BaseModule


def max_left(bb):
    return min(bb[0], bb[2], bb[4], bb[6])

def max_right(bb):
    return max(bb[0], bb[2], bb[4], bb[6])

def row_bbs(bbs, texts):
    bbs_clusters = [(b, t) for b, t in zip(bbs, texts)]
    bbs_clusters.sort(key=lambda x: max_left(x[0]))
    
    clusters, y_min, cluster_texts = [], [], []
    for tgt_node, text in bbs_clusters:
        if len (clusters) == 0:
            clusters.append([tgt_node])
            cluster_texts.append([text])
            y_min.append(tgt_node[1])
            continue
        matched = None
        tgt_7_1 = tgt_node[7] - tgt_node[1]
        min_tgt_0_6 = min(tgt_node[0], tgt_node[6])
        max_tgt_2_4 = max(tgt_node[2], tgt_node[4])
        max_left_tgt = max_left(tgt_node)
        for idx, clt in enumerate(clusters):
            src_node = clt[-1]
            src_5_3 = src_node[5] - src_node[3]
            max_src_2_4 = max(src_node[2], src_node[4])
            min_src_0_6 = min(src_node[0], src_node[6])
            overlap_y = (src_5_3 + tgt_7_1) - (max(src_node[5], tgt_node[7]) - min(src_node[3], tgt_node[1]))
            overlap_x = (max_src_2_4 - min_src_0_6) + (max_tgt_2_4 - min_tgt_0_6) - (max(max_src_2_4, max_tgt_2_4) - min(min_src_0_6, min_tgt_0_6))
            if overlap_y > 0.4*min(src_5_3, tgt_7_1) and overlap_x < 0.6*min(max_src_2_4 - min_src_0_6, max_tgt_2_4 - min_tgt_0_6):
                distance = max_left_tgt - max_right(src_node)
                if matched is None or distance < matched[1]:
                    matched = (idx, distance)
        if matched is None:
            clusters.append([tgt_node])
            cluster_texts.append([text])
            y_min.append(tgt_node[1])
        else:
            idx = matched[0]
            cluster_texts[idx].append(text)
            clusters[idx].append(tgt_node)
    zip_clusters = list(zip(clusters, y_min, cluster_texts))
    zip_clusters.sort(key=lambda x: x[1])
    return zip_clusters


class DocumentGenerator(BaseModule):
    instance = None
    
    def __init__(self, common_config, model_config):
        super(DocumentGenerator, self).__init__(common_config, model_config)
        
        
    @staticmethod
    def get_instance(common_config, model_config):
        if DocumentGenerator.instance is None:
            DocumentGenerator.instance = DocumentGenerator(common_config, model_config)
        return DocumentGenerator.instance


    @total_time
    def predict(self, request_id, inp, out, metadata):
        result = inp.get_data()
        
        for page_index in range(len(result['pages'])):
            result['pages'][page_index]['text'] = ''
            # group texts
            texts = result['pages'][page_index]['raw_words']
            text_boxes = result['pages'][page_index]['text_boxes'].reshape(-1, 8)
            page_texts = []
            # get avg_h
            list_hs = []
            for _, y1, _, y2, _, y3, _, y4 in text_boxes:
                ymin = min(y1, y2, y3, y4)
                ymax = max(y1, y2, y3, y4)
                list_hs.append(ymax - ymin)
            avg_h = np.average(list_hs)
            
            zip_clusters = row_bbs(text_boxes, texts)
            for bbs, _, texts in zip_clusters:
                line_text = []
                if len(texts) > 0:
                    line_text.append(texts[0])
                for i in range(1, len(texts)):
                    c_xmin = min(bbs[i][0], bbs[i][2], bbs[i][4], bbs[i][6])
                    l_xmax = max(bbs[i-1][0], bbs[i-1][2], bbs[i-1][4], bbs[i-1][6])
                    pad = (c_xmin - l_xmax)/avg_h
                    if pad < 0.1 and re.search('[\.|\,]$', texts[i-1]) is not None:
                        pass
                    elif pad > -0.2:
                        line_text.append(' ' * max(math.ceil(pad), 1))
                    try:
                        if re.search('^[\.|\,]', texts[i]) is not None and len(line_text) >= 2 and line_text[-1] == ' ' and line_text[-2] != ' ' is not None:
                            line_text = line_text[:-1]
                    except:
                        pass
                        # pdb.set_trace()
                    line_text.append(texts[i])
                page_texts.append(''.join(line_text))
            page_texts = '\n'.join(page_texts)
            result['pages'][page_index]['text'] = page_texts
        out.set_data(result)
        return out, metadata
