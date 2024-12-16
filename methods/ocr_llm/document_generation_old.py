import re
import pdb
import cv2
import numpy as np

from utils.utils import total_time
from modules.base import BaseModule


def sort_box(bbs, texts):
    bbs_clusters = [(b, t) for b, t in zip(bbs, texts)]
    bbs_clusters.sort(key=lambda x: x[0][0])

    # group cluster 1st time
    clusters, y_min, cluster_texts = [], [], []
    for tgt_node, text  in bbs_clusters:
        if len (clusters) == 0:
            clusters.append([tgt_node])
            cluster_texts.append([text])
            y_min.append(tgt_node[1])
            continue
        matched = None
        for idx, clt in enumerate(clusters):
            src_node = clt[-1]
            overlap_y = ((src_node[3] - src_node[1]) + (tgt_node[3] - tgt_node[1])) - (max(src_node[3], tgt_node[3]) - min(src_node[1], tgt_node[1]))
            overlap_x = ((src_node[2] - src_node[0]) + (tgt_node[2] - tgt_node[0])) - (max(src_node[2], tgt_node[2]) - min(src_node[0], tgt_node[0]))
            distance = tgt_node[0] - src_node[2]
            if overlap_y > 0.8*min(src_node[3] - src_node[1], tgt_node[3] - tgt_node[1]) and overlap_x < 0.6*min(src_node[2] - src_node[0], tgt_node[2] - tgt_node[0]):
                if matched is None or distance < matched[1]:
                    matched = (idx, distance)
        if matched is None:
            clusters.append([tgt_node])
            cluster_texts.append([text])
            y_min.append(tgt_node[1])
        else:
            idx = matched[0]
            clusters[idx].append(tgt_node)
            cluster_texts[idx].append(text)
    zip_clusters = list(zip(clusters, y_min, cluster_texts))
    zip_clusters.sort(key=lambda x: x[1])
    return zip_clusters


def break_lines(zip_clusters, d_thres):
    # break lines
    page_text_lines = []
    page_bb_lines = []
    for bb_cluster in zip_clusters:
        bbs, _, texts = bb_cluster
        text_lines = []
        bb_lines = []
        text_line = []
        bb_line = []
        for bb, text in zip(bbs, texts):
            if len(text_line) == 0:
                text_line.append(text)
                bb_line.append(bb)
            else:
                if bb[0] - bb_line[-1][2] > d_thres:
                    text_lines.append(text_line)
                    bb_lines.append(bb_line)
                    text_line = [text]
                    bb_line = [bb]
                else:
                    text_line.append(text)
                    bb_line.append(bb)
        if len(text_line) != 0:
            text_lines.append(text_line)
            bb_lines.append(bb_line)
        for text_line, bb_line in zip(text_lines, bb_lines):
            bb_line = np.array(bb_line)
            xmin = np.min(bb_line[:, 0])
            ymin = np.min(bb_line[:, 1])
            xmax = np.max(bb_line[:, 2])
            ymax = np.max(bb_line[:, 3])
            page_text_lines.append(' '.join(text_line))
            page_bb_lines.append([xmin, ymin, xmax, ymax])
    return page_text_lines, page_bb_lines


def overlap_x(bb1, bb2):
    xmin1, xmax1 = bb1[0], bb1[2]
    xmin2, xmax2 = bb2[0], bb2[2]
    overlap = (((xmax1 - xmin1) + (xmax2 - xmin2)) - (max(xmax1, xmax2) - min(xmin1, xmin2)))/min(xmax1 - xmin1, xmax2 - xmin2)
    if overlap > 0.2:
        return True
    return False


def overlap_y(bb1, bb2):
    ymin1, ymax1 = bb1[1], bb1[3]
    ymin2, ymax2 = bb2[1], bb2[3]
    overlap = (((ymax1 - ymin1) + (ymax2 - ymin2)) - (max(ymax1, ymax2) - min(ymin1, ymin2)))/min(ymax1 - ymin1, ymax2 - ymin2)
    if overlap > 0.2:
        return True
    return False



class DocumentGenerator(BaseModule):
    instance = None
    
    def __init__(self, common_config, model_config):
        super(DocumentGenerator, self).__init__(common_config, model_config)
        
        
    @staticmethod
    def get_instance(common_config, model_config):
        if DocumentGenerator.instance is None:
            DocumentGenerator.instance = DocumentGenerator(common_config, model_config)
        return DocumentGenerator.instance


    def text_to_lines(self, page_text_lines, page_bb_lines, avg_h):
        list_groups = [[i] for i in range(len(page_bb_lines))]
        return list_groups


    def text_to_groups(self, page_text_lines, page_bb_lines, avg_h):
        ### merge text chunk into groups
        x_ds = []
        for i in range(len(page_bb_lines)):
            ds = []
            for j in range(len(page_bb_lines)):
                if i == j:
                    ds.append(0)
                elif page_bb_lines[j][0] >= page_bb_lines[i][0]:
                    ds.append(page_bb_lines[j][0] - page_bb_lines[i][2])
                else:
                    ds.append(page_bb_lines[i][0] - page_bb_lines[j][2])
            x_ds.append(ds)

        y_ds = []
        for i in range(len(page_bb_lines)):
            ds = []
            for j in range(len(page_bb_lines)):
                if i == j:
                    ds.append(0)
                elif page_bb_lines[j][1] >= page_bb_lines[i][1]:
                    ds.append(page_bb_lines[j][1] - page_bb_lines[i][3])
                else:
                    ds.append(page_bb_lines[i][1] - page_bb_lines[j][3])
            y_ds.append(ds)
        # merge by distance
        threshold_x = 1. * avg_h
        threshold_y = 0.5 * avg_h
        list_groups = [[i] for i in range(len(page_bb_lines))]
        is_merge = True
        while is_merge and len(list_groups) > 1:
            is_merge = False
            for i in range(len(list_groups)-1):
                for j in range(i+1, len(list_groups)):
                    for index_i in list_groups[i]:
                        for index_j in list_groups[j]:
                            if (y_ds[index_i][index_j] <= threshold_y and overlap_x(page_bb_lines[index_i], page_bb_lines[index_j])) or (x_ds[index_i][index_j] <= threshold_x and overlap_y(page_bb_lines[index_i], page_bb_lines[index_j])):
                                is_merge = True
                                list_groups[i] += list_groups[j]
                                list_groups.pop(j)
                                break
                        if is_merge:
                            break
                    if is_merge:
                        break
                if is_merge:
                    break
        
        # merge by rule
        is_merge = True
        while is_merge and len(list_groups) > 1:
            is_merge = False
            for i, group in enumerate(list_groups):
                num_marker = 0
                for j in group:
                    text = page_text_lines[j]
                    if re.search('\:$', text) is not None:
                        num_marker += 1
                if num_marker/len(group) > 0.65:
                    list_merge_indexes = []
                    for j in range(len(list_groups)):
                        if j != i:
                            for k in range(len(list_groups[j])):
                                if list_groups[j][k] < list_groups[i][-1] and list_groups[j][k] > list_groups[i][0]:
                                    list_merge_indexes.append(j)
                                    break
                    if len(list_merge_indexes) != 0:
                        is_merge = True
                        list_merge_indexes.sort(key = lambda x: -x)
                        for index in list_merge_indexes:
                            list_groups[i] += list_groups[index]
                            list_groups.pop(index)
        return list_groups


    @total_time
    def predict(self, request_id, inp, out, metadata):
        result = inp.get_data()
        
        for page_index in range(len(result['pages'])):
            result['pages'][page_index]['text'] = ''
            # group texts
            texts = result['pages'][page_index]['raw_words']
            bbs = []
            for text_box in result['pages'][page_index]['text_boxes']:
                xmin = min(text_box[..., 0])
                xmax = max(text_box[..., 0])
                ymin = min(text_box[..., 1])
                ymax = max(text_box[..., 1])
                bbs.append([xmin, ymin, xmax, ymax])
            # get avg_h
            list_hs = []
            for x1, y1, x2, y2 in bbs:
                list_hs.append(y2 - y1)
            avg_h = np.average(list_hs)
            zip_clusters = sort_box(bbs, texts)
            page_text_lines, page_bb_lines = break_lines(zip_clusters, 2*avg_h)
            if result['merge_type'] == 'group':
                list_group_indexes = self.text_to_groups(page_text_lines, page_bb_lines, avg_h)
            else:
                list_group_indexes = self.text_to_lines(page_text_lines, page_bb_lines, avg_h)
            group_texts = []
            group_bbs = []
            for group_indexes in list_group_indexes:
                group_text = []
                group_bb = [10000, 10000, 0, 0]
                for index in group_indexes:
                    group_text.append(page_text_lines[index])
                    x1, y1, x2, y2 = page_bb_lines[index]
                    group_bb[0] = min(group_bb[0], x1)
                    group_bb[1] = min(group_bb[1], y1)
                    group_bb[2] = max(group_bb[2], x2)
                    group_bb[3] = max(group_bb[3], y2)
                group_bbs.append(group_bb)
                group_texts.append('\n'.join(group_text))
            # merge text groups with html table
            zip_clusters = sort_box(group_bbs, group_texts)
            page_texts = []
            for bb_cluster in zip_clusters:
                _, _, texts = bb_cluster
                page_texts += texts
            page_texts = '\n'.join(page_texts)
            result['pages'][page_index]['text'] = page_texts
        pdb.set_trace()
        out.set_data(result)
        return out, metadata
