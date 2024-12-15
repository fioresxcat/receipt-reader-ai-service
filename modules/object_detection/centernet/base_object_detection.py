import pdb
import cv2
import numpy as np

from utils.utils import total_time
from modules.base_module import BaseModule


class BaseObjectDetector(BaseModule):
    def __init__(self, common_config, model_config):
        super(BaseObjectDetector, self).__init__(common_config, model_config)
        
    
    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        # top-right have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        # return the ordered coordinates
        return rect  # tl, br, tr, bl order

    
    def expand_point(self, pts, img_size:tuple):
        pts = self.order_points(pts)
        x_dist = [pts[0][0], img_size[0] - pts[1][0], img_size[0] - pts[2][0], pts[3][0]]
        y_dist = [pts[0][1], pts[1][1], img_size[1] - pts[2][1], img_size[1] - pts[3][1]]
        delta_x = np.min(x_dist)
        delta_y = np.min(y_dist)
        pts = [(pts[0][0] - delta_x, pts[0][1] - delta_y), (pts[1][0] + delta_x, pts[1][1] - delta_y),
            (pts[2][0]+delta_x, pts[2][1]+delta_y), (pts[3][0]-delta_x, pts[3][1]+delta_y)]
        return np.array(pts, dtype='float32')
    
    def four_point_transform(self, image, pts):
        (tl, tr, br, bl) = pts
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
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        # compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(pts, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        # return the warped image
        return warped

