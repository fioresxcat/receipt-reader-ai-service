import pdb
import cv2
import heapq
import unidecode
import numpy as np

from collections import Counter

from .utils import sort_bbs, softmax
from modules.base_module import BaseModule
from utils.utils import total_time



class InformationExtractor(BaseModule):
    def __init__(self, common_config, model_config):
        super(InformationExtractor, self).__init__(common_config, model_config)
                               
    
    def normalize_bbox(self, bbox, width, height):
        return [
             int(1000 * (bbox[0] / width)),
             int(1000 * (bbox[1] / height)),
             int(1000 * (bbox[2] / width)),
             int(1000 * (bbox[3] / height)),
        ]
    
    
    def to_4_points(self, box):
        x1, y1, x2, y2, x3, y3, x4, y4 = box
        xmin = min(x1, x2, x3, x4)
        xmax = max(x1, x2, x3, x4)
        ymin = min(y1, y2, y3, y4)
        ymax = max(y1, y2, y3, y4)
        return [int(xmin), int(ymin), int(xmax), int(ymax)]
    
    
    def gen_annotation_for_img(self,
                               image,
                               raw_orig_polys,
                               raw_words,
                               mask_type='unmasked', 
                               widen_range_x=[0.1, 0.2], 
                               widen_range_y=[0.1, 0.25], 
                               disable_marker=False, 
                               remove_accent=True, 
                               augment=False):
        
        img_h, img_w, _ = image.shape
        normalized_boxes, words= [], []
        for raw_word, raw_poly in zip(raw_words, raw_orig_polys):
            if remove_accent:
                words.append(unidecode.unidecode(raw_word.lower()))
            else:
                words.append(raw_word.lower())
            xmin = np.min(raw_poly[:, 0])
            xmax = np.max(raw_poly[:, 0])
            ymin = np.min(raw_poly[:, 1])
            ymax = np.max(raw_poly[:, 1])
            normalized_boxes.append(self.normalize_bbox((xmin, ymin, xmax, ymax), img_w, img_h))
        return words, raw_orig_polys, normalized_boxes
    

    def predict_page(self, image, bbs_raw, raw_words):
        words, orig_polys, normalized_boxes = self.gen_annotation_for_img(image, bbs_raw, raw_words)
        preds_val = None
        img_w, img_h, _ = image.shape

        # encode input for model
        encoded_inputs = self.processor(image, words, boxes=normalized_boxes, truncation=True, stride=128, padding="max_length", max_length=512, return_overflowing_tokens=True, return_offsets_mapping=True, return_tensors="np")

        wordidx2label = {}
        for idx in range(len(encoded_inputs['input_ids'])):
            input_ids = encoded_inputs['input_ids'][idx:idx+1]
            bbox = encoded_inputs['bbox'][idx:idx+1]
            attention_mask = encoded_inputs['attention_mask'][idx:idx+1]
            pixel_values = np.array(encoded_inputs['pixel_values'][idx:idx+1])
            output_dict = self.request_multi([input_ids, bbox, attention_mask, pixel_values])
            outputs = np.array(output_dict.as_numpy(self.model_config['output_name']))
            # process output
            output = outputs[0]
            preds_val = output.tolist()
            words_idx = encoded_inputs.words(idx)
            for i, (pred, wordidx) in enumerate(zip(preds_val, words_idx)):
                if wordidx is None:
                    continue
                if wordidx not in wordidx2label:
                    wordidx2label[wordidx] = [np.argmax(pred)]
                else:
                    wordidx2label[wordidx].append(np.argmax(pred))

        wordidx2label = {wordidx: Counter(label).most_common(1)[0][0] for wordidx, label in wordidx2label.items()}
        labels = []
        for i in range(len(words)):
            if i in wordidx2label.keys():
                labels.append(self.id2label[wordidx2label[i]])
            else:
                labels.append('text')
        return labels


    def predict_page_prob(self, image, bbs_raw, raw_words):
        """
            bbs_raw and raw_words are already in sorted order (from top to bottom, left to right)
        """
        words, orig_polys, normalized_boxes = self.gen_annotation_for_img(image, bbs_raw, raw_words)
        n_words = len(raw_words)
        preds_val = None
        img_w, img_h, _ = image.shape

        # encode input for model
        encoded_inputs = self.processor(image, words, boxes=normalized_boxes, truncation=True, stride=128, padding="max_length", max_length=512, return_overflowing_tokens=True, return_offsets_mapping=True, return_tensors="np")
        batch_word_ids = [encoded_inputs.word_ids(i) for i in range(encoded_inputs['bbox'].shape[0])]
        wordidx2pred = {}
        for idx in range(0, n_words):
            wordidx2pred[idx] = {
                'results': [[] for _ in range(len(batch_word_ids))],
                'final_result': None
            }

        for batch_idx in range(len(encoded_inputs['input_ids'])):
            input_ids = encoded_inputs['input_ids'][batch_idx:batch_idx+1]
            bbox = encoded_inputs['bbox'][batch_idx:batch_idx+1]
            attention_mask = encoded_inputs['attention_mask'][batch_idx:batch_idx+1]
            pixel_values = np.array(encoded_inputs['pixel_values'][batch_idx:batch_idx+1])
            output_dict = self.request_multi([input_ids, bbox, attention_mask, pixel_values])
            outputs = np.array(output_dict.as_numpy(self.model_config['output_name']))
            # process output
            logits = outputs[0]    # tensor shape (512, 18)
            probs = softmax(logits)   # tensor shape (512, 18)
            word_ids = batch_word_ids[batch_idx]    # a list of len = 512
            input_ids = encoded_inputs['input_ids'][batch_idx]  # a tensor shape (512,)
            for token_idx, (pred, word_idx) in enumerate(zip(probs, word_ids)):
                if word_idx is None:
                    continue
                token = self.processor.decode(input_ids[token_idx])
                top_indices = np.argsort(pred)[::-1][:3]
                top_values = pred[top_indices]
                highest_probs = {}
                for (idx, val) in zip(top_indices, top_values):
                    highest_probs[self.label_list[idx]] = val
                wordidx2pred[word_idx]['results'][batch_idx].append({
                    'token': token,
                    'top_scores': highest_probs,
                    'best_scores': (np.argmax(pred), np.max(pred))
                })

        for word_idx, pred_info in wordidx2pred.items():
            results = pred_info['results']
            results = [token_res for ls_token_res in results for token_res in ls_token_res]
            if len(results) == 0:
                final_field, final_score = 'text', 1
            else:
                field2scores = {}
                for token_res in results:
                    for field, score in token_res['top_scores'].items():
                        if field in field2scores:
                            field2scores[field].append(score)
                        else:
                            field2scores[field] = [score]
                field2score = {field: np.sum(scores) / len(results) for field, scores in field2scores.items()}
                final_field, final_score = max(field2score.items(), key=lambda x: x[1])
                second_field, second_score = heapq.nlargest(2, field2score.items(), key=lambda x: x[1])[-1]

            wordidx2pred[word_idx]['final_result'] = (
                final_field,
                min(final_score + 0.05, 1.0)
            )
        # to list
        labels = []
        for i in range(len(wordidx2pred)):
            labels.append(wordidx2pred[i]['final_result'])
        return labels
