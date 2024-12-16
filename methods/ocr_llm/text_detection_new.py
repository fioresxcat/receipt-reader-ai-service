import pdb
import cv2
import math
import numpy as np
import unidecode

from utils import total_time
from modules.text_detection_db.base_text_detection import BaseTextDetector


def poly2box(poly):
    poly = np.array(poly).flatten().tolist()
    xmin, xmax = min(poly[::2]), max(poly[::2])
    ymin, ymax = min(poly[1::2]), max(poly[1::2])
    return xmin, ymin, xmax, ymax


def max_left(poly):
    return min(poly[0], poly[2], poly[4], poly[6])

def max_right(poly):
    return max(poly[0], poly[2], poly[4], poly[6])

def row_polys(polys):
    polys.sort(key=lambda x: max_left(x))
    clusters, y_min = [], []
    for tgt_node in polys:
        if len (clusters) == 0:
            clusters.append([tgt_node])
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
            if overlap_y > 0.5*min(src_5_3, tgt_7_1) and overlap_x < 0.6*min(max_src_2_4 - min_src_0_6, max_tgt_2_4 - min_tgt_0_6):
                distance = max_left_tgt - max_right(src_node)
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


def row_bbs(bbs):
    polys = []
    poly2bb = {}
    for bb in bbs:
        poly = [bb[0], bb[1], bb[2], bb[1], bb[2], bb[3], bb[0], bb[3]]
        polys.append(poly)
        poly2bb[tuple(poly)] = bb
    poly_rows = row_polys(polys)
    bb_rows = []
    for row in poly_rows:
        bb_row = []
        for poly in row:
            bb_row.append(poly2bb[tuple(poly)])
        bb_rows.append(bb_row)
    return bb_rows


def sort_bbs(bbs):
    bb2idx_original = {tuple(bb): i for i, bb in enumerate(bbs)}
    bb_rows = row_bbs(bbs)
    sorted_bbs = [bb for row in bb_rows for bb in row]
    sorted_indexes = [bb2idx_original[tuple(bb)] for bb in sorted_bbs]
    return sorted_bbs, sorted_indexes


def sort_polys(polys):
    poly2idx_original = {tuple(poly):i for i, poly in enumerate(polys)}
    poly_clusters = row_polys(polys)
    sorted_polys = []
    for row in poly_clusters:
        sorted_polys.extend(row)
    sorted_indexes = [poly2idx_original[poly] for poly in sorted_polys]
    return sorted_polys, sorted_indexes



def str_similarity(str1, str2, normalize=False, remove_space=True):
    import Levenshtein
    import re
    
    str1 = str1.lower()
    str2 = str2.lower()
    if normalize:
        str1 = unidecode.unidecode(str1)
        str2 = unidecode.unidecode(str2)
    if remove_space:
        str1 = re.sub(r'\s+', '', str1)
        str2 = re.sub(r'\s+', '', str2)

    distance = Levenshtein.distance(str1, str2)
    score = 1 - (distance / (max(len(str1), len(str2))))
    return score


class TextDetector(BaseTextDetector):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(TextDetector, self).__init__(common_config, model_config)
        self.box_thresh = model_config['box_thresh']

        
    @staticmethod
    def get_instance(common_config, model_config):
        if TextDetector.instance is None:
            TextDetector.instance = TextDetector(common_config, model_config)
        return TextDetector.instance


    def merge_boxes(self, boxes_4p, boxes_8p):
        bbs_clusters = [(box4, box8) for box4, box8 in zip(boxes_4p, boxes_8p)]
        bbs_clusters.sort(key=lambda x: x[0][0])
        new_boxes_4p, new_boxes_8p = [], []
        for tgt_node, tgt_node_8p  in bbs_clusters:
            if len(new_boxes_4p) == 0:
                new_boxes_4p.append(tgt_node)
                new_boxes_8p.append(tgt_node_8p)
                continue
            matched = None
            for idx, src_node in enumerate(new_boxes_4p):
                overlap_y = ((src_node[3] - src_node[1]) + (tgt_node[3] - tgt_node[1])) - (max(src_node[3], tgt_node[3]) - min(src_node[1], tgt_node[1]))
                overlap_x = ((src_node[2] - src_node[0]) + (tgt_node[2] - tgt_node[0])) - (max(src_node[2], tgt_node[2]) - min(src_node[0], tgt_node[0]))
                if overlap_y > 0.9*min(src_node[3] - src_node[1], tgt_node[3] - tgt_node[1]) and overlap_x > 0.2*min(src_node[3] - src_node[1], tgt_node[3] - tgt_node[1]):
                    distance = tgt_node[0] - src_node[2]
                    if matched is None or distance < matched[1]:
                        matched = (idx, distance)
            if matched is None:
                new_boxes_4p.append(tgt_node)
                new_boxes_8p.append(tgt_node_8p)
            else:
                idx = matched[0]
                x1, y1, x2, y2 = new_boxes_4p[idx]
                x3, y3, x4, y4 = tgt_node
                xmin = min(x1, x2, x3, x4)
                ymin = min(y1, y2, y3, y4)
                xmax = max(x1, x2, x3, x4)
                ymax = max(y1, y2, y3, y4)
                new_boxes_4p[idx] = [xmin, ymin, xmax, ymax]
                new_boxes_8p[idx] = [xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax]
        return new_boxes_4p, new_boxes_8p


    @total_time
    def predict(self, request_id, inp, out, metadata):
        result = inp.get_data()
        result['pages'] = []
        for page_index in range(len(result['images'])):
            # run text detect
            p8_bbs = []
            p4_bbs = []
            text_box_images = []
            src_image = result['images'][page_index].copy()
            image = cv2.cvtColor(src_image, cv2.COLOR_BGR2RGB)

            h, w = image.shape[:2]
            image = self.resize_image(image, image_short_side=960)
            image = np.expand_dims(image[..., ::-1], 0)
            image = image.transpose((0, 3, 1, 2))  # BGR to RGB, BHWC to BCHW, (n, 3, h, w)
            image_input = np.ascontiguousarray(image, dtype='uint8')  # contiguous

            output_dict = self.request(image_input)
            metadata = self.add_metadata(metadata, 1, 1)
            p = np.array(output_dict.as_numpy(self.model_config['output_name']))[0]
            p = p.transpose((1, 2, 0))
            bitmap = p > 0.3
            bbs, scores = self.polygons_from_bitmap(p, bitmap, w, h, box_thresh=self.box_thresh, max_candidates=-1, unclip_ratio=1.2)
            # change to 8 value
            list_h = []
            for bb in bbs:
                x1, y1 = bb[0]
                x2, y2 = bb[1]
                x3, y3 = bb[2]
                x4, y4 = bb[3]
                xmin = min(x1, x2, x3, x4)
                xmax = max(x1, x2, x3, x4)
                ymin = min(y1, y2, y3, y4)
                ymax = max(y1, y2, y3, y4)
                p8_bbs.append((x1, y1, x2, y2, x3, y3, x4, y4))
                p4_bbs.append((xmin, ymin, xmax, ymax))
                list_h.append(ymax - ymin)
            # remove too small box
            avg_h = np.mean(list_h)
            new_p8_bbs = []
            new_p4_bbs = []
            for i in range(len(p4_bbs)):
                xmin, ymin, xmax, ymax = p4_bbs[i]
                if (ymax - ymin) < 0.4 * avg_h:
                    continue
                new_p8_bbs.append(p8_bbs[i])
                new_p4_bbs.append(p4_bbs[i])
            
            p4_bbs, p8_bbs = self.merge_boxes(new_p4_bbs, new_p8_bbs)
            for x1, y1, x2, y2, x3, y3, x4, y4 in p8_bbs:
                pts = self.expand_long_box(src_image, x1, y1, x2, y2, x3, y3, x4, y4)
                edge_s, edge_l = self.get_edge(x1, y1, x2, y2, x3, y3, x4, y4)
                if edge_l / edge_s < 1.5:
                    text_image = self.to_2_points(src_image, x1, y1, x2, y2, x3, y3, x4, y4)
                else:
                    text_image = self.four_point_transform(src_image, pts)
                text_box_images.append(text_image)
            
            # add text detect output to page info
            result['pages'].append({
                'text_boxes': np.array(p8_bbs).reshape(-1, 4, 2),
                'text_box_images': text_box_images
            })
        out.set_data(result)
        return out, metadata
