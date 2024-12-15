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


    @total_time
    def predict(self, request_id, inp, out, metadata):
        result = inp.get_data()
        result['list_list_boxes'] = []
        result['list_bbs'] = []
        result['list_bbs_raw'] = []
        for i in range(len(result['rotated_images'])):
            src_image = result['rotated_images'][i]
            h, w = src_image.shape[:2]
            image = cv2.cvtColor(src_image.copy(), cv2.COLOR_BGR2RGB)
            image = self.resize_image(image, image_short_side=640)
            batch_images = np.expand_dims(image, 0).transpose((0, 3, 1, 2))
            output_dict = self.request(batch_images)
            metadata = self.add_metadata(metadata, 1, 1)
            p = np.array(output_dict.as_numpy(self.model_config['output_name']))[0].transpose((1, 2, 0))
            bitmap = p > self.p_thresh
            boxes, scores = self.polygons_from_bitmap(p, bitmap, w, h, max_candidates=-1, box_thresh=self.box_thresh)
            # bbs = self.expand_boxes(boxes)
            bbs = boxes
            # change to 8 value
            new_bbs = []
            bbs_raw = bbs
            for bb in bbs:
                x1, y1 = bb[0]
                x2, y2 = bb[1]
                x3, y3 = bb[2]
                x4, y4 = bb[3]
                new_bbs.append((x1, y1, x2, y2, x3, y3, x4, y4))

            list_boxes = []
            for box, new_box in zip(bbs_raw, new_bbs):
                edge_s, edge_l = self.get_edge(new_box)
                if edge_l / edge_s < 1.5:
                    text_image = self.to_2_points(src_image, new_box)
                else:
                    # pts = self.expand_long_box(image, new_box)
                    text_image = self.four_point_transform(src_image, box)
                list_boxes.append(text_image)
            result['list_list_boxes'].append(list_boxes)
            result['list_bbs'].append(new_bbs)
            result['list_bbs_raw'].append(bbs_raw)
        out.set_data(result)
        return out, metadata

    