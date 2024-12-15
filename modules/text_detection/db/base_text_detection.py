import pdb
import cv2
import math
import pyclipper
import numpy as np

from shapely.geometry import Polygon

from utils.utils import total_time
from modules.base_module import BaseModule


class BaseTextDetector(BaseModule):
    def __init__(self, common_config, model_config):
        super(BaseTextDetector, self).__init__(common_config, model_config)
        
        
    def resize_image(self, image, image_short_side):
        h, w = image.shape[:2]
        if h < w:
            h_new = image_short_side
            w_new = int(w / h * h_new / 32) * 32
        else:
            w_new = image_short_side
            h_new = int(h / w * w_new / 32) * 32
        resized_img = cv2.resize(image, (w_new, h_new))
        return resized_img    

    
    def box_score_fast(self, bitmap, _box):
        h, w = bitmap.shape[:2]
        box = _box.copy()
        xmin = np.clip(np.floor(box[:, 0].min()).astype(np.int32), 0, w - 1)
        xmax = np.clip(np.ceil(box[:, 0].max()).astype(np.int32), 0, w - 1)
        ymin = np.clip(np.floor(box[:, 1].min()).astype(np.int32), 0, h - 1)
        ymax = np.clip(np.ceil(box[:, 1].max()).astype(np.int32), 0, h - 1)

        mask = np.zeros((ymax - ymin + 1, xmax - xmin + 1), dtype=np.uint8)
        box[:, 0] = box[:, 0] - xmin
        box[:, 1] = box[:, 1] - ymin
        cv2.fillPoly(mask, box.reshape(1, -1, 2).astype(np.int32), 1)
        return cv2.mean(bitmap[ymin:ymax + 1, xmin:xmax + 1], mask)[0], xmax-xmin, ymax-ymin
    
    
    def unclip(self, box, unclip_ratio=1.5):
        poly = Polygon(box)
        subject = [tuple(l) for l in box]
        w = box[:, 0].max() - box[:, 0].min()
        h = box[:, 1].max() - box[:, 1].min()
        distance = poly.area * unclip_ratio / poly.length
        offset = pyclipper.PyclipperOffset()
        offset.AddPath(subject, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        expanded = offset.Execute(distance)
        return expanded, distance
    
    
    def get_mini_boxes(self, contour):
        bounding_box = cv2.minAreaRect(contour)
        points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

        index_1, index_2, index_3, index_4 = 0, 1, 2, 3
        if points[1][1] > points[0][1]:
            index_1 = 0
            index_4 = 1
        else:
            index_1 = 1
            index_4 = 0
        if points[3][1] > points[2][1]:
            index_2 = 2
            index_3 = 3
        else:
            index_2 = 3
            index_3 = 2

        box = [points[index_1], points[index_2],
               points[index_3], points[index_4]]
        return box, min(bounding_box[1])
    
    
    def polygons_from_bitmap(self, pred, bitmap, dest_width, dest_height, max_candidates=100, box_thresh=0.7):
        height, width = bitmap.shape[:2]
        boxes, scores = [], []

        contours, _ = cv2.findContours((bitmap * 255.0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        distance_4, distance_6, distance_8, distance_12 = [], [], [], []
        for contour in contours:
            epsilon =  0.002* cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            points = approx.reshape((-1, 2))
            if points.shape[0] < 4:
                continue
            score, w_box, h_box = self.box_score_fast(pred, points.reshape((-1, 2)))
            if box_thresh > score:
                continue

            if points.shape[0] > 2:
                # unclip_ratio=1.6
                if w_box / h_box < 4: 
                    unclip_ratio = 1.6
                elif w_box / h_box < 8: 
                    unclip_ratio = 1.8
                elif w_box / h_box < 12:
                    unclip_ratio = 2.2
                else: unclip_ratio = 2.5
                # print(unclip_ratio)
                box, distance = self.unclip(points, unclip_ratio=unclip_ratio)
                # rate = w_box / h_box
                # if rate < 4: pass 
                # elif rate < 6: distance_4.append(distance)
                # elif rate < 8: distance_6.append(distance)
                # elif rate < 12: distance_8.append(distance)
                # else: distance_12.append(distance)
                if len(box) > 1:
                    continue
            else:
                continue
            box = np.array(box).reshape(-1, 2)
            if len(box) == 0: continue
            box, sside = self.get_mini_boxes(box.reshape((-1, 1, 2)))
            if sside < 5:
                continue
            box = np.array(box)
            box[:, 0] = np.clip(box[:, 0] / width * dest_width, 0, dest_width)
            box[:, 1] = np.clip(box[:, 1] / height * dest_height, 0, dest_height)
            boxes.append(box.astype('int32'))
            scores.append(score)
        # print(distance_4, '\n', distance_6,'\n', distance_8,'\n', distance_12)
        if max_candidates == -1:
            return boxes, scores
        idxs = np.argsort(scores)
        scores = [scores[i] for i in idxs[:max_candidates]]
        boxes = [boxes[i] for i in idxs[:max_candidates]]

        return boxes, scores
    
    
    # def expand_boxes(self, boxes):
    #     new_boxes = []
    #     for box in boxes:
    #         box = np.array(box)
    #         box_h = max(box[3][1] - box[0][1], box[2][1] - box[1][1])
    #         box_w = max(box[1][0] - box[0][0], box[2][0] - box[3][0])
    #         if box_w / box_h < 4.0: 
    #             new_boxes.append(box)
    #             continue
    #         box[:2, 1] -= int(box_h * 10/100)
    #         box[2:, 1] += int(box_h * 10/100)
    #         new_boxes.append(box)
    #     return new_boxes
    
    
    def expand_boxes(self, boxes):
        new_boxes = []
        for box in boxes:
            box = np.array(box)
            box_h = max(box[3][1] - box[0][1], box[2][1] - box[1][1])
            box_w = max(box[1][0] - box[0][0], box[2][0] - box[3][0])
            if box_w / box_h < 6.0: 
                new_boxes.append(box)
                continue
            elif box_w / box_h < 12.0:
                delta_h = math.ceil(box_h * 0.1)
            else:
                delta_h = math.ceil(box_h * 0.2)
            box[:2, 1] -= delta_h
            box[2:, 1] += delta_h
            box[[0, 3], 0] -= delta_h
            box[[1, 2], 0] += delta_h
            new_boxes.append(box)
        return new_boxes
        

    def order_points(self, pts):
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype = "float32")
        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        # return the ordered coordinates
        return rect

        
    def four_point_transform(self, image, pts):
        # obtain a consistent order of the points and unpack them
        # individually
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect
        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")
        # compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        return warped
    
    def get_edge(self, bb):
        x1, y1, x2, y2, x3, y3, x4, y4 = bb
        e1 = math.sqrt(abs(x2 - x1)**2 + abs(y2 - y1)**2)
        e2 = math.sqrt(abs(x3 - x2)**2 + abs(y3 - y2)**2)
        e3 = math.sqrt(abs(x4 - x3)**2 + abs(y4 - y3)**2)
        e4 = math.sqrt(abs(x1 - x4)**2 + abs(y1 - y4)**2)
        edge_s = min([e1, e2, e3, e4])
        edge_l = max([e1, e2, e3, e4])
        return edge_s, edge_l
    

    def to_2_points(self, image, bb):
        x1, y1, x2, y2, x3, y3, x4, y4 = bb
        xmin = min(x1, x2, x3, x4)
        xmax = max(x1, x2, x3, x4)
        ymin = min(y1, y2, y3, y4)
        ymax = max(y1, y2, y3, y4)
        field_image = image[ymin:ymax, xmin:xmax]
        return field_image
    
    
    def expand_long_box(self, image, pts):
        x1, y1, x2, y2, x3, y3, x4, y4 = pts
        h, w, _ = image.shape
        box_h = max(y4 - y1, y3 - y2)
        box_w = max(x2 - x1, x3 - x4)
        if box_w / box_h >= 6:
            # expand_pxt = math.ceil((0.05 + ((box_w / box_h - 5)/5)*0.05) * box_h)
            expand_pxt = math.ceil(0.1 * box_h)
            x1 = max(0, x1 - expand_pxt)
            x2 = min(w, x2 + expand_pxt)
            x3 = min(w, x3 + expand_pxt)
            x4 = max(0, x4 - expand_pxt)
            y1 = max(0, y1 - expand_pxt)
            y2 = max(0, y2 - expand_pxt)
            y3 = min(h, y3 + expand_pxt)
            y4 = min(h, y4 + expand_pxt)
        pts = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
        return pts
