import pdb
import cv2
import math
import numpy as np

from utils.utils import total_time
from modules.text_detection.db.base_text_detection import BaseTextDetector


class TextDetector(BaseTextDetector):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(TextDetector, self).__init__(common_config, model_config)
        self.box_thresh = self.model_config['box_thresh']
        self.p_thresh = self.model_config['p_thresh']
        self.unclip_ratio = self.model_config['unclip_ratio']
        
    
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
        result['images'] = result.pop('rotated_images', None)
        for page_index in range(len(result['images'])):
            src_image = result['images'][page_index]
            h, w = src_image.shape[:2]
            image = cv2.cvtColor(src_image.copy(), cv2.COLOR_BGR2RGB)
            image = self.resize_image(image, image_short_side=640)
            batch_images = np.expand_dims(image, 0).transpose((0, 3, 1, 2))
            output_dict = self.request(batch_images)
            metadata = self.add_metadata(metadata, 1, 1)
            p = np.array(output_dict.as_numpy(self.model_config['output_name']))[0].transpose((1, 2, 0))
            bitmap = p > self.p_thresh
            bbs, scores = self.polygons_from_bitmap(p, bitmap, w, h, max_candidates=-1, box_thresh=self.box_thresh)
            # change to 8 value
            p8_bbs = []
            p4_bbs = []
            text_box_images = []
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
                pts = self.expand_long_box(src_image, (x1, y1, x2, y2, x3, y3, x4, y4))
                edge_s, edge_l = self.get_edge((x1, y1, x2, y2, x3, y3, x4, y4))
                if edge_l / edge_s < 1.5:
                    text_image = self.to_2_points(src_image, (x1, y1, x2, y2, x3, y3, x4, y4))
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

    