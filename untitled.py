import pdb
import os
import cv2
import numpy as np
from pathlib import Path
import json
import base64
import shutil
from utils.utils import total_time
from modules.object_detection.yolov8.base_object_detection import BaseObjectDetector, LetterBox
from modules.base_module import BaseModule


def is_image(fp):
    fp = str(fp)
    return fp.endswith('.jpg') or fp.endswith('.png') or fp.endswith('.jpeg') or fp.endswith('.JPG') or fp.endswith('.JPEG') or fp.endswith('.PNG')


class CornerDetector(BaseObjectDetector):
    instance = None
    
    def __init__(self, common_config, model_config):
        super(CornerDetector, self).__init__(common_config, model_config)
        self.letterbox = LetterBox((model_config['input_shape'][0], model_config['input_shape'][1]), auto=False, stride=32)
        
        
    @staticmethod
    def get_instance(common_config, model_config):
        if CornerDetector.instance is None:
            CornerDetector.instance = CornerDetector(common_config, model_config)
        return CornerDetector.instance
    
    
    def predict(self, inp, out):
        result = inp.get_data()
        batch_images = []
        warped_images = []
        
        for raw_image in result['images']:
            orig_img = raw_image.copy()
            h, w, _ = orig_img.shape
            resize_img = cv2.resize(raw_image, (self.model_config['input_shape'][0], self.model_config['input_shape'][0]), interpolation = cv2.INTER_LINEAR)
            image = np.transpose(resize_img, (2, 0, 1))
            batch_images.append(image)

        batch_images_length = len(batch_images)
        batch_images = np.array(batch_images).astype(np.float32)
        outputs = []
        if len(batch_images) != 0:
            index = 0
            while index < len(batch_images):
                output_dict = self.request(batch_images[index:index+self.model_config['max_batch_size']])
                outputs.append(np.array(output_dict.as_numpy(self.model_config['output_name'])))
                index += self.model_config['max_batch_size']
            outputs = np.concatenate(outputs, axis=0)
            outputs = outputs[:batch_images_length]

        for i in range(len(outputs)):
            output = np.clip(outputs[0], a_min = 0, a_max = 1.0) 
            # convert to points of original image
            list_pts = [int(float(p) * w) if i % 2 == 0 else int(float(p) * h)for i, p in enumerate(output)]
            pts = [(list_pts[i], list_pts[i + 1]) for i in range(0, self.model_config['num_point'] * 2, 2)]
            pts = np.array(pts)
            # cut invoice from original image
            cut_image = self.four_point_transform(result['images'][i], pts)
            warped_images.append(cut_image)
        result['warped_images'] = warped_images
        out.set_data(result)
        return out




class ReceiptRotator(BaseModule):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(ReceiptRotator, self).__init__(common_config, model_config)
        self.class_names = {0: 'Rotate0', 1: 'Rotate180', 2: 'Rotate270', 3: 'Rotate90'}

    
    @staticmethod
    def get_instance(common_config, model_config):
        if ReceiptRotator.instance is None:
            ReceiptRotator.instance = ReceiptRotator(common_config, model_config)
        return ReceiptRotator.instance

    
    def __resize(self, image, IMAGE_SIZE):
        height, width, _ = image.shape
        if width < height:
            if width > IMAGE_SIZE:
                image = cv2.resize(image, (IMAGE_SIZE, height * IMAGE_SIZE // width))
            else:
                image = cv2.resize(image, (IMAGE_SIZE, height * IMAGE_SIZE // width), interpolation = cv2.INTER_AREA)
        else :
            if height > IMAGE_SIZE:
                image = cv2.resize(image, (width * IMAGE_SIZE // height, IMAGE_SIZE))
            else:
                image = cv2.resize(image, (width * IMAGE_SIZE // height, IMAGE_SIZE), interpolation = cv2.INTER_AREA)
        return image
    
    
    def __crop_center(self, image):
        height, width, _ = image.shape
        delta = abs(height - width) // 2

        if width < height:
            img_cropped = image[delta : delta + width, : , :]
        else:
            img_cropped = image[: , delta : delta + height, :]

        return img_cropped
    
    
    def softmax(self, x):
        """Compute softmax values for each sets of scores in x."""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0) # only difference
    
    
    def predict(self, inp, out):
        result = inp.get_data()
        batch_images = []
        rotated_images = []

        for raw_image in result['warped_images']:
            image = raw_image.copy()
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = self.__resize(img, self.model_config['input_shape'][0])
            img = self.__crop_center(img)
            img = np.moveaxis(img, -1, 0)
            batch_images.append(img)

        batch_images_length = len(batch_images)
        batch_images = np.array(batch_images)
        outputs = []
        if len(batch_images) != 0:
            index = 0
            while index < len(batch_images):
                output_dict = self.request(batch_images[index:index+self.model_config['max_batch_size']])
                outputs.append(np.array(output_dict.as_numpy(self.model_config['output_name'])))
                index += self.model_config['max_batch_size']
            outputs = np.concatenate(outputs, axis=0)
            outputs = outputs[:batch_images_length]

        for i, output in enumerate(outputs):
            output = self.softmax(output)
            pred_label = self.class_names[np.argmax(output)]
            if pred_label == 'Rotate0':
                rotate_img = result['warped_images'][i]
            elif pred_label == 'Rotate180':
                rotate_img = cv2.rotate(result['warped_images'][i], cv2.ROTATE_180)
            elif pred_label == 'Rotate270':
                rotate_img = cv2.rotate(result['warped_images'][i], cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif pred_label == 'Rotate90':
                rotate_img = cv2.rotate(result['warped_images'][i], cv2.ROTATE_90_CLOCKWISE)
            rotated_images.append(rotate_img)
        result['rotated_images'] = rotated_images
        out.set_data(result)
        return out


def warp_and_rotate():
    import utils
    from inpout import Input, Output

    config_env = utils.load_yaml('configs/config_env.yaml')
    config_methods = utils.load_yaml('configs/config_methods.yaml')
    config_models = utils.load_yaml('configs/config_models.yaml')
    config_common = utils.load_yaml('configs/config_common.yaml')

    corner_detector = CornerDetector(config_env['inference_server'], config_models['triton_models']['corner_detection'])
    rotator = ReceiptRotator(config_env['inference_server'], config_models['triton_models']['receipt_rotation'])
    dir = 'test_files/receipt_data-test_cThao'
    for ip in Path(dir).rglob('*'):
        if not is_image(ip):
            continue
        with open(ip, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read())
        nparr = np.fromstring(base64.b64decode(base64_string), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # warp
        inp = Input(data = {'images': [image]})
        out = corner_detector.predict(inp, Output())

        # rotate
        out = rotator.predict(out, Output())

        result = out.get_data()
        rotated_img = result['rotated_images'][0]

        # save
        save_path = str(ip).replace('/receipt_data-test_cThao/', '/receipt_data-test_cThao_warped/')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, rotated_img)
        print(f'done {ip}')


if __name__ == '__main__':
    pass
    # warp_and_rotate()