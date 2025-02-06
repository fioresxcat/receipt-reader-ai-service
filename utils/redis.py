import pdb
import cv2
import base64
import numpy as np
import redis
from .utils import base64_to_image


error_dict = {
    201: 'Redis Write FAILED',
    202: 'Redis Read FAILED',
    203: 'Request ID not in Redis',
}


def key_with_prefix(key):
    return 'ReceiptOCR-' + key


def check_redis_connection(redis_db):
    try:
        redis_db.ping()
        return True
    except redis.exceptions.ConnectionError as e:
        return False
    except Exception as e:
        raise e


def to_redis(root_logger, log_data, redis_db, timeout):
    try:
        pipeline = redis_db.pipeline()
        for key, value in log_data:
            redis_key = key_with_prefix(key)
            pipeline.set(redis_key, value, timeout)
        pipeline.execute()
    except Exception as e:
        err_code = 201
        root_logger.error(error_dict[err_code], extra={
            'metadata': {
                'redis_keys': [key for key, _ in log_data],
                'error': str(e),
            },
        })
        return err_code

    return 0


def in_redis(root_logger, redis_db, key):
    key = key_with_prefix(key)
    try:
        is_exist = redis_db.exists(key)
        return 0, is_exist
    except Exception as e:
        err_code = 202
        root_logger.error(error_dict[err_code], extra={
                          'metadata': {'redis_key': key, 'error': str(e)}})
        return err_code, False


def get_redis_value(logger, redis_db, redis_key):
    try:
        value = redis_db.get(redis_key)
    except:
        err_code = 202
        logger.error(error_dict[err_code], extra={
            'metadata': {'key': redis_key}
        })
        return err_code, None
    if value is None:
        err_code = 203
        logger.error(error_dict[err_code], extra={
            'metadata': {'key': redis_key}
        })
        return err_code, None
    
    return 0, value



def load_images_from_redis(logger, redis_db, request_id):
    err_code, num_images = get_redis_value(logger, redis_db, redis_key=key_with_prefix(f'{request_id}-num_images'))
    if err_code != 0:
        return err_code, None
    num_images = int(num_images.decode())
    images = []
    for i in range(num_images):
        redis_key = key_with_prefix(f'{request_id}-raw_image-{i}')
        err_code, b64_im = get_redis_value(logger, redis_db, redis_key)
        if err_code != 0:
            return err_code, None
        im = base64_to_image(b64_im)
        images.append(im)
    return 0, images
    


def remove_key_redis(logger, redis_db, request_id):
    # get all keys of a request_id
    remove_keys = []
    err_code, num_images = get_redis_value(logger, redis_db, redis_key=key_with_prefix(f'{request_id}-num_images'))
    if err_code != 0:
        return err_code, None
    remove_keys.append(key_with_prefix(f'{request_id}-num_images'))
    num_images = int(num_images.decode())
    for i in range(num_images):
        remove_keys.append(key_with_prefix(f'{request_id}-raw_image-{i}'))
    redis_db.delete(*remove_keys)
    