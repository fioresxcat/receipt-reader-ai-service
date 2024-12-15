import os
import re
import cv2
import yaml
import base64
import logging
import numpy as np

from datetime import datetime


env_pattern = re.compile(r".*?\${(.*?)}.*?")
def env_constructor(loader, node):
    value = loader.construct_scalar(node)
    for group in env_pattern.findall(value):
        value = value.replace(f"${{{group}}}", os.environ.get(group))
    return value

yaml.add_implicit_resolver("!pathex", env_pattern)
yaml.add_constructor("!pathex", env_constructor)


def base64_to_image(string_bytes):
    im_bytes = base64.b64decode(string_bytes)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
    image = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    return image


def list_base64_to_images(list_string_bytes):
    images = []
    for string_bytes in list_string_bytes:
        im_bytes = base64.b64decode(string_bytes)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
        image = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        images.append(image)
    return images


def load_yaml(yaml_path):
    data = yaml.load(open(yaml_path, 'r'))
    return data


def total_time(predict):
    def wrapper(self, request_id, inp, out, metadata):
        start = datetime.now()
        res = predict(self, request_id, inp, out, metadata)
        end = datetime.now()
        self.time_logger.info('request_id=' + str(request_id) + ',' + type(self).__name__ + ' predict time: ' + str(end - start))
        return res
    return wrapper


