import os
import pdb

from modules.base_module import BaseModule
from utils.utils import total_time


class BaseInformationExtractor(BaseModule):
    def __init__(self, common_config, model_config):
        super(BaseInformationExtractor, self).__init__(common_config, model_config)
    
    
    def sort_box(self, bbs, texts, labels, cands):
        bbs_clusters = [(b, t, l, c) for b, t, l, c in zip(bbs, texts, labels, cands)]
        bbs_clusters.sort(key=lambda x: x[0][0])

        clusters, y_min, cluster_texts, cluster_labels, cluster_cands = [], [], [], [], []
        for tgt_node, text, label, cand  in bbs_clusters:
            if len (clusters) == 0:
                clusters.append([tgt_node])
                cluster_texts.append([text])
                cluster_labels.append([label])
                cluster_cands.append([cand])
                y_min.append(tgt_node[1])
                continue
            matched = None
            for idx, clt in enumerate(clusters):
                src_node = clt[-1]
                overlap_y = ((src_node[3] - src_node[1]) + (tgt_node[3] - tgt_node[1])) - (max(src_node[3], tgt_node[3]) - min(src_node[1], tgt_node[1]))
                overlap_x = ((src_node[2] - src_node[0]) + (tgt_node[2] - tgt_node[0])) - (max(src_node[2], tgt_node[2]) - min(src_node[0], tgt_node[0]))
                if overlap_y > 0.8*min(src_node[3] - src_node[1], tgt_node[3] - tgt_node[1]) and overlap_x < 0.6*min(src_node[2] - src_node[0], tgt_node[2] - tgt_node[0]):
                    distance = tgt_node[0] - src_node[2]
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
    
    
    def get_raw_fields(self, bb_clusters):
        raw_ocrs = {}
        raw_cands = {}
        coordinates = {}
        for label in self.label_list:
            raw_ocrs[label] = []
            raw_cands[label] = []
            coordinates[label] = []
        for bb_cluster in bb_clusters:
            bbs, _, texts, labels, cands = bb_cluster
            for bb, text, label, cand in zip(bbs, texts, labels, cands):
                raw_ocrs[label].append(text)
                raw_cands[label].append(cand)
                coord = bb
                if len(coordinates[label]) == 0:
                    coordinates[label] = coord
                else:
                    c_xmin, c_ymin, c_xmax, c_ymax = coordinates[label]
                    new_coord = [min(c_xmin, coord[0]), min(c_ymin, coord[1]), max(c_xmax, coord[2]), max(c_ymax, coord[3])]
                    coordinates[label] = new_coord
        return raw_ocrs, raw_cands, coordinates
    
    
    @total_time
    def predict(self, request_id, inp, out, metadata):
        result = inp.get_data()
        list_raw_ocrs = []
        list_raw_cands = []
        list_coordinates = []
        for i, page_info in enumerate(result['pages']):
            bbs = [bb.tolist() for bb in result['boxes'][i]['boxes']]
            labels = [self.label_list[int(index)] for index in result['boxes'][i]['class_ids']]
            texts = result['pages'][i]['raw_words']
            cands = result['pages'][i]['raw_cands']
            bb_clusters = self.sort_box(bbs, texts, labels, cands)
            raw_ocrs, raw_cands, coordinates = self.get_raw_fields(bb_clusters)
            list_raw_ocrs.append(raw_ocrs)
            list_raw_cands.append(raw_cands)
            list_coordinates.append(coordinates)
        result['raw_ocrs'] = list_raw_ocrs
        result['raw_cands'] = list_raw_cands
        result['coordinates'] = list_coordinates
        metadata = self.add_metadata(metadata, 1, 1)
        out.set_data(result)
        return out, metadata
            


