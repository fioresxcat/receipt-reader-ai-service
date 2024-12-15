import os
import pdb
import cv2
import pickle
import numpy as np 
import tensorflow as tf 


def max_left(bb):
    return min(bb[0], bb[2], bb[4], bb[6])

def max_right(bb):
    return max(bb[0], bb[2], bb[4], bb[6])

def row_bbs(bbs_classes_labels):
    bbs_classes_labels.sort(key=lambda x: max_left(x[0]))
    clusters, y_min, cluster_texts, cluster_labels = [], [], [], []
    for tgt_node, text, label in bbs_classes_labels:
        if len (clusters) == 0:
            clusters.append([tgt_node])
            cluster_texts.append([text])
            cluster_labels.append([label])
            y_min.append(tgt_node[1])
            continue
        matched = None
        for idx, clt in enumerate(clusters):
            src_node = clt[-1] 
            overlap_y = ((src_node[5] - src_node[3]) + (tgt_node[7] - tgt_node[1])) - (max(src_node[5], tgt_node[7]) - min(src_node[3], tgt_node[1]))
            overlap_x = (max(src_node[2], src_node[4]) - min(src_node[0], src_node[6])) + (max(tgt_node[2], tgt_node[4]) - min(tgt_node[0], tgt_node[6])) - (max(src_node[2], src_node[4], tgt_node[2], tgt_node[4]) - min(src_node[0], src_node[6], tgt_node[0], tgt_node[6]))
            if overlap_y > 0.5*min(src_node[5] - src_node[3], tgt_node[7] - tgt_node[1]) and overlap_x < 0.6*min(max(src_node[2], src_node[4]) - min(src_node[0], src_node[6]), max(tgt_node[2], tgt_node[4]) - min(tgt_node[0], tgt_node[6])):
                distance = max_left(tgt_node) - max_right(src_node)
                if matched is None or distance < matched[1]:
                    matched = (idx, distance)
        if matched is None:
            clusters.append([tgt_node])
            cluster_texts.append([text])
            cluster_labels.append([label])
            y_min.append(tgt_node[1])
        else:
            idx = matched[0]
            clusters[idx].append(tgt_node)
            cluster_texts[idx].append(text)
            cluster_labels[idx].append(label)
    zip_clusters = list(zip(clusters, y_min, cluster_texts, cluster_labels))
    zip_clusters.sort(key=lambda x: x[1])
    return zip_clusters
        

def sort_bbs(bbs, texts, labels):
    bbs_classes_labels = [(b, c, l) for b, c, l in zip(bbs, texts, labels)]
    bb_clusters = row_bbs(bbs_classes_labels)
    pdb.set_trace()
    return bb_clusters

