import pdb
import cv2
import base64
import numpy as np
from .utils import base64_to_image


def to_redis(log_data, redis_db, timeout):
    try:
        for key, value in log_data:
            redis_db.set('SCANIT_' + key, value)
            redis_db.expire('SCANIT_' + key, timeout)
    except:
        return {'error_code': 201, 'error_msg': 'failed to connect to redis'}
    return {'error_code': 0, 'error_msg': 'OK'}


def from_redis(redis_db, request_id):
    try:
        num_images_value = redis_db.get('SCANIT_' + request_id + '_num_images')
        paper_type = redis_db.get('SCANIT_' + request_id + '_paper_type')
    except:
        return {'error_code': 201, 'error_msg': 'failed to connect to redis'}, None
    if num_images_value is None or paper_type is None:
        return {'error_code': 202, 'error_msg': 'no request_id key in redis'}, None
    num_images = int(num_images_value.decode())
    paper_type = paper_type.decode()
    images = []
    for i in range(num_images):
        try:
            im_b64 = redis_db.get('SCANIT_' + request_id + '_rotatedimage:' + str(i))
        except:
            return {'error_code': 201, 'error_msg': 'failed to connect to redis'}, None
        if im_b64 is None:
            return {'error_code': 202, 'error_msg': 'no request_id key in redis'}, None
        image = base64_to_image(im_b64)
        images.append(image)
    return {'error_code': 0, 'error_msg': 'OK'}, images, paper_type


def remove_key_redis(redis_db, request_id):
    # get all keys of a request_id
    list_delete_keys = []
    try:
        num_images_value = redis_db.get('SCANIT_' + request_id + '_num_images')
        paper_type = redis_db.get('SCANIT_' + request_id + '_paper_type')
        list_delete_keys.append('SCANIT_' + request_id + '_num_images')
        list_delete_keys.append('SCANIT_' + request_id + '_paper_type')
    except:
        return {'error_code': 201, 'error_msg': 'failed to connect to redis'}, None
    if num_images_value is None:
        return {'error_code': 202, 'error_msg': 'no request_id key in redis'}, None
    num_images = int(num_images_value.decode())
    for i in range(num_images):
        list_delete_keys.append('SCANIT_' + request_id + '_rotatedimage:' + str(i))
    # delelte all key of a request_id
    for key in list_delete_keys:
        try:
            res = redis_db.delete(key)
        except:
            continue
