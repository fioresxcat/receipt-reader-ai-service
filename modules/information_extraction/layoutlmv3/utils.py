import os
import re
import pdb
import unidecode
import numpy as np


def max_left(bb):
    return min(bb[0], bb[2], bb[4], bb[6])

def max_right(bb):
    return max(bb[0], bb[2], bb[4], bb[6])

def row_bbs(bbs_classes_labels):
    bbs_classes_labels.sort(key=lambda x: max_left(x[0]))
    clusters, y_min, cluster_texts, cluster_labels, cluster_cands = [], [], [], [], []
    for tgt_node, text, label, cand in bbs_classes_labels:
        if len (clusters) == 0:
            clusters.append([tgt_node])
            cluster_texts.append([text])
            cluster_labels.append([label])
            cluster_cands.append([cand])
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
            cluster_texts.append([text])
            cluster_labels.append([label])
            cluster_cands.append([cand])
            y_min.append(tgt_node[1])
        else:
            idx = matched[0]
            clusters[idx].append(tgt_node)
            cluster_texts[idx].append(text)
            cluster_labels[idx].append(label)
            cluster_cands[idx].append(cand)
    zip_clusters = list(zip(clusters, y_min, cluster_texts, cluster_labels, cluster_cands))
    zip_clusters.sort(key=lambda x: x[1])
    return zip_clusters

def sort_bbs(bbs, texts, labels, cands):
    """
        bbs: list of bbs in page
        texts: list of texts corresponding to bbs
        labels: list of labels corresponding to bbs
        cands: list of raw ocr outputs (each cand is a list, each element in each cand is a tensor of shape (223,) that represent the output of model for each character in the word)
    """
    bbs_classes_labels = [(b, c, l, cand) for b, c, l, cand in zip(bbs, texts, labels, cands)]
    bb_clusters = row_bbs(bbs_classes_labels)
    return bb_clusters


def box_normalize(bbs, raw_words, bbs_raw, raw_cands):
    """
        not to normalize box in range (0, 1) but the purpose is to remove abnormal box
    """
    # find avg height of all bbs
    list_h = []
    for bb in bbs:
        h = [bb[1], bb[3], bb[5], bb[7]]
        list_h.append(max(h) - min(h))
    avg_h = 0
    if len(list_h) != 0:
        avg_h = sum(list_h)/len(list_h)
    # remove abnormal box
    new_bbs, new_raw_words, new_bbs_raw, new_raw_cands = [], [], [], []
    for bb, raw_word, bb_raw, raw_cand in zip(bbs, raw_words, bbs_raw, raw_cands):
        lh = [bb[1], bb[3], bb[5], bb[7]]
        h = max(lh) - min(lh)
        if (h < 0.3*avg_h or h > 1.5*avg_h) and (re.sub('[^\d|a-z]', '', raw_word.lower()) == ''):
            pass
        else:
            new_bbs.append(bb)
            new_raw_words.append(raw_word)
            new_bbs_raw.append(bb_raw)
            new_raw_cands.append(raw_cand)
    return new_bbs, new_raw_words, new_bbs_raw, new_raw_cands, avg_h


def softmax(arr):
   e_x = np.exp(arr)
   return (e_x.transpose()/np.sum(e_x, axis=-1)).transpose()
