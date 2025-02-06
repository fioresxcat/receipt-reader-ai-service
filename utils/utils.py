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


def image_to_base64(image: np.ndarray, format: str = 'png') -> str:
    """
    Convert a numpy.ndarray image to a base64-encoded string.

    Args:
        image (np.ndarray): The image as a numpy array.
        format (str): The image format to encode ('png' or 'jpg').

    Returns:
        str: The base64-encoded string representation of the image.
    """
    # Ensure the image is in the correct format (e.g., 8-bit, 3-channel for color images)
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    # Encode the image to a byte stream
    if format.lower() == 'png':
        _, buffer = cv2.imencode('.png', image)
    elif format.lower() == 'jpg':
        _, buffer = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # Adjust JPEG quality if needed
    else:
        raise ValueError("Unsupported image format. Use 'png' or 'jpg'.")

    # Convert the byte stream to a base64 string
    base64_str = base64.b64encode(buffer).decode('utf-8')
    return base64_str


def load_yaml(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def total_time(predict):
    def wrapper(self, request_id, inp, out, metadata):
        start = datetime.now()
        res = predict(self, request_id, inp, out, metadata)
        end = datetime.now()
        self.time_logger.info('request_id=' + str(request_id) + ',' + type(self).__name__ + ' predict time: ' + str(end - start))
        return res
    return wrapper



