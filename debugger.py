import os 
import cv2
import pdb
import json
import numpy as np

class Debugger(object):
    def __init__(self, log_path='logs'):
        self.log_path = log_path
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path, exist_ok=True)


    def log_SpamDetector(self, inp_data, out_data, log_path):
        if len(inp_data['rule_code']) != 0:
            with open(os.path.join(log_path, 'appcheck.json'), 'w') as f:
                json.dump({'rule_code': inp_data['rule_code'], 'rule_msg': inp_data['rule_msg']}, f)

    
    def log_FraudDetector(self, inp_data, out_data, log_module_path, log_path):
        with open(os.path.join(log_module_path, 'texture.json'), 'w') as f:
            json.dump({'label': inp_data['fraud_texture']['label'], 'score': inp_data['fraud_texture']['score']}, f)
        with open(os.path.join(log_module_path, 'device.json'), 'w') as f:
            json.dump({'label': inp_data['fraud_device']['label'], 'score': inp_data['fraud_device']['score']}, f)
        if len(inp_data['rule_code']) != 0:
            with open(os.path.join(log_path, 'appcheck.json'), 'w') as f:
                json.dump({'rule_code': inp_data['rule_code'], 'rule_msg': inp_data['rule_msg']}, f)

    
    def log_InformationExtractor(self, inp_data, out_data, log_module_path):
        # log json
        image = inp_data['rotated_image']
        labels = inp_data['box_labels']
        bbs2idx_sorted= inp_data['bbs2idx_sorted']
        bb2text = inp_data['bb2text']
        h, w, _ = image.shape
        __version__= "4.6.0"
        flags= {}
        shapes= []
        imagePath= 'refined_image.png'
        imageData= None
        imageHeight= h
        imageWidth= w
        for bb in bb2text.keys():
            x1, y1, x2, y2, x3, y3, x4, y4 = bb
            label = labels[bbs2idx_sorted[bb]]
            text = bb2text[bb]
            new_shape = {
                "label": label,
                "points": [
                    [int(x1), int(y1)],
                    [int(x2), int(y2)],
                    [int(x3), int(y3)],
                    [int(x4), int(y4)]
                ],
                "group_id": None,
                "shape_type": "polygon",
                "text": text,
                "flags": {}
            }
            shapes.append(new_shape)

        new_data = dict(
            version=__version__,
            flags=flags,
            shapes=shapes,
            imagePath=imagePath,
            imageData=imageData,
            imageHeight=imageHeight,
            imageWidth=imageWidth,
        )
        with open(os.path.join(log_module_path, 'log.json'), 'w') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        # log images
        for fieldname in inp_data['raw_list_box'].keys():
            if fieldname == 'products':
                for i, product in enumerate(inp_data['raw_list_box']['products']):
                    for sub_fieldname in product.keys():
                        for j, image in enumerate(inp_data['raw_list_box']['products'][i][sub_fieldname]):
                            cv2.imwrite(os.path.join(log_module_path, fieldname + '_' + str(i) + '_' + sub_fieldname + '_' + str(j) + '.jpg'), image)
            else:
                for i, image in enumerate(inp_data['raw_list_box'][fieldname]):
                    cv2.imwrite(os.path.join(log_module_path, fieldname + '_' + str(i) + '.jpg'), image)
                    
                    
    def log_InformationExtractorA4(self, inp_data, out_data, log_module_path):
        # log json
        for page_index in range(len(inp_data['rotated_images'])):
            image = inp_data['rotated_images'][page_index]
            labels = inp_data['list_box_labels'][page_index]
            bbs2idx_sorted= inp_data['list_bbs2idx_sorted'][page_index]
            bb2text = inp_data['list_bb2text'][page_index]
            h, w, _ = image.shape
            __version__= "4.6.0"
            flags= {}
            shapes= []
            imagePath= 'refined_image_' + str(page_index) + '.png'
            imageData= None
            imageHeight= h
            imageWidth= w
            for bb in bb2text.keys():
                x1, y1, x2, y2, x3, y3, x4, y4 = bb
                label = labels[bbs2idx_sorted[bb]]
                text = bb2text[bb]
                new_shape = {
                    "label": label,
                    "points": [
                        [int(x1), int(y1)],
                        [int(x2), int(y2)],
                        [int(x3), int(y3)],
                        [int(x4), int(y4)]
                    ],
                    "group_id": None,
                    "shape_type": "polygon",
                    "text": text,
                    "flags": {}
                }
                shapes.append(new_shape)

            new_data = dict(
                version=__version__,
                flags=flags,
                shapes=shapes,
                imagePath=imagePath,
                imageData=imageData,
                imageHeight=imageHeight,
                imageWidth=imageWidth,
            )
            with open(os.path.join(log_module_path, 'log_' + str(page_index) + '.json'), 'w') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            # log images
            for fieldname in inp_data['list_raw_list_box'][page_index].keys():
                if fieldname == 'products':
                    for i, product in enumerate(inp_data['list_raw_list_box'][page_index]['products']):
                        for sub_fieldname in product.keys():
                            for j, image in enumerate(inp_data['list_raw_list_box'][page_index]['products'][i][sub_fieldname]):
                                cv2.imwrite(os.path.join(log_module_path, str(page_index) + '_' + fieldname + '_' + str(i) + '_' + sub_fieldname + '_' + str(j) + '.jpg'), image)
                else:
                    for i, image in enumerate(inp_data['list_raw_list_box'][page_index][fieldname]):
                        cv2.imwrite(os.path.join(log_module_path, str(page_index) + '_' + fieldname + '_' + str(i) + '.jpg'), image)

    
    def log_module(self, request_id, inp, out, module_name):
        # create dirs
        if not os.path.exists(os.path.join(self.log_path, request_id)):
            os.makedirs(os.path.join(self.log_path, request_id), exist_ok=True)
        log_path = os.path.join(self.log_path, request_id)
        log_module_path = os.path.join(self.log_path, request_id, module_name)
        if not os.path.exists(log_module_path):
            os.makedirs(log_module_path, exist_ok=True)
        # write to debug dir
        inp_data = inp.get_data()
        out_data = out.get_data()
        print('MODULE NAME: ', module_name)
        # pdb.set_trace()
        if module_name == 'SpamDetector':
            for i, image in enumerate(inp_data['images']):
                cv2.imwrite(os.path.join(log_path, 'image_' + str(i) + '.png'), image)
            self.log_SpamDetector(inp_data, out_data, log_path)
        elif module_name == 'FraudDetector':
            self.log_FraudDetector(inp_data, out_data, log_module_path, log_path)
        elif module_name in ['CornerDetector', 'A4CornerDetector']:
            for i, image in enumerate(inp_data['images']):
                cv2.imwrite(os.path.join(log_path, 'image_' + str(i) + '.png'), image)
            if 'warped_images' in inp_data.keys():
                for i, warped_image in enumerate(inp_data['warped_images']):
                    cv2.imwrite(os.path.join(log_path, 'warped_image_' + str(i) + '.png'), warped_image)
            else:
                self.log_SpamDetector(inp_data, out_data, log_path)
        elif module_name in ['ReceiptRotator', 'A4Rotator']:
            for i, rotated_image in enumerate(inp_data['rotated_images']):
                cv2.imwrite(os.path.join(log_path, 'rotated_image_' + str(i) + '.png'), rotated_image)
        elif module_name in ['ReceiptAngleEstimator', 'A4AngleEstimator']:
            for i, rotated_image in enumerate(inp_data['rotated_images']):
                cv2.imwrite(os.path.join(log_path, 'refined_image_' + str(i) + '.png'), rotated_image)
        # elif module_name == 'InformationExtractor':
        #     self.log_InformationExtractorA4(inp_data, out_data, log_module_path)
        # elif module_name == 'InformationExtractorA4':
        #     self.log_InformationExtractorA4(inp_data, out_data, log_module_path)
        elif module_name == 'PostProcessor':
            with open(os.path.join(log_path, 'result.json'), 'w') as f:
                json.dump(out_data['result'], f, ensure_ascii=False, indent=2)
            # pdb.set_trace()
            for index, image in enumerate(inp_data['rotated_images']):
                save_path = os.path.join(log_path, 'image_' + str(index) + '.png')
                cv2.imwrite(save_path, image)
        elif module_name == 'LLMPostprocessor':
            for index, image in enumerate(inp_data['images']):
                save_path = os.path.join(log_path, 'image_' + str(index) + '.png')
                cv2.imwrite(save_path, image)
            result = {}
            for group in out_data:
                if group['group_name'] == 'general_info':
                    for key in group['infos']:
                        result[key] = group['infos'][key][0]
                elif group['group_name'] == 'product_info':
                    if 'products' not in result:
                        result['products'] = []
                    product_info = {}
                    for key in group['infos']:
                        product_info[key] = group['infos'][key][0]
                    result['products'].append(product_info)

            with open(os.path.join(log_path, 'result.json'), 'w') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            
