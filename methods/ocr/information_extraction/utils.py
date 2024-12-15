import numpy as np
import copy
import re


def get_bb_from_poly(poly, img_w, img_h):
    x1, y1, x2, y2, x3, y3, x4, y4 = poly    # tl -> tr -> br -> bl
    xmin = min (x1, x2, x3, x4)
    xmin = max(0, min(xmin, img_w))
    xmax = max (x1, x2, x3, x4)
    xmax = max(0, min(xmax, img_w))
    ymin = min (y1, y2, y3, y4)
    ymin = max(0, min(ymin, img_h))
    ymax = max (y1, y2, y3, y4)
    ymax = max(0, min(ymax, img_h))

    return xmin, ymin, xmax, ymax


def max_left(bb):
    return min(bb[0], bb[2], bb[4], bb[6])


def max_right(bb):
    return max(bb[0], bb[2], bb[4], bb[6])


def get_manual_text_feature(text: str):
    feature = []

    # có phải ngày tháng không
    feature.append(int(re.search('(\d{1,2})\/(\d{1,2})\/(\d{4})', text) != None))

    # co phai gio khong
    feature.append(int(re.search('(\d{1,2}):(\d{1,2})', text) != None))
        
    # có phải ma hang hoa khong
    feature.append(int(re.search('^\d+$', text) != None and len(text) > 5))

    # có phải tiền dương không
    feature.append(int(re.search('^\d{1,3}(\,\d{3})*(\,00)+$', text.replace('.', ',')) != None or re.search('^\d{1,3}(\,\d{3})+$', text.replace('.', ',')) != None))
    
    # co phai tien am khong
    feature.append(int(text.startswith('-') and re.search('^[\d(\,)]+$', text[1:].replace('.', ',')) != None and len(text) >= 3))

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


def row_bbs(bbs):
    bbs.sort(key=lambda x: max_left(x))
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
            y_min.append(tgt_node[1])
        else:
            idx = matched[0]
            clusters[idx].append(tgt_node)
    zip_clusters = list(zip(clusters, y_min))
    zip_clusters.sort(key=lambda x: x[1])
    zip_clusters = list(np.array(zip_clusters, dtype=object)[:, 0])
    return zip_clusters

