import os
import re
import pdb
import cv2
import math
import copy
import json
import asyncio
import numpy as np

from openai import OpenAI
from datetime import datetime
from json_repair import repair_json
from transformers import AutoTokenizer

from utils.utils import total_time
from modules.base_vllm import BaseModuleVLLM

from pydantic import BaseModel, ConfigDict, Field, create_model
from typing import Optional, Literal, Dict, Any, List



class LLMInformationExtractor(BaseModuleVLLM):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(LLMInformationExtractor, self).__init__(common_config, model_config)
        self.my_dir = os.path.dirname(__file__)
        self.tokenizer = AutoTokenizer.from_pretrained(os.path.join(self.my_dir, self.model_config['base_model_name']))
        self.general_fields = {
            # 'mart_address': """Địa chỉ của cửa hàng/Siêu thị phát hành hoá đơn này.""",
            'mart_name': """Tên của cửa hàng/Siêu thị phát hành hoá đơn này.""",
            'pos_id': """Mã/Số của quầy in hoá đơn, thường được viết là Quầy, Pos.""",
            'receipt_id': """Dãy số hoặc ký tự xác định hóa đơn, thường theo sau \"Số hoá đơn\" hoặc \"Số HĐ\" hoặc \"HĐ\" hoặc \"Số giao dịch\" hoặc \"Ticket\" hoặc tương tự.""",
            'staff': """Tên hoặc mã số của thu ngân/nhân viên in hoá đơn, theo sau từ \"thu ngân\" hoặc \"nhân viên\" hoặc tương tự.""",
            'date': """Ngày in hoá đơn, trả về theo định dạng dd/mm/yyyy.""",
            'time': """Thời gian theo hh:mm:ss in hoá đơn.""",
            'total_quantity': """Tổng số lượng sản phẩm của hoá đơn.""",
            'total_money': """Tổng tiền của hoá đơn sau giảm giá/Số tiền mà khách hàng phải trả.""",
            # 'total_original_money': """Tổng tiền của hoá đơn trước khi giảm giá/Tổng tiền của tất cả sản phẩm trong hoá đơn.""",
            # 'total_discount_money': """Tổng số tiền được giảm giá/Tổng của số tiền giảm giá của từng sản phầm.""",
            # 'mart_type': """Tên của chuỗi siêu thị mà cửa hàng/siêu thị này thuộc về."""
        }

        self.product_fields = {
            'product_id': """Mã SKU của sản phẩm/mặt hàng.""",
            'product_name': """Tên của sản phẩm/mặt hàng.""",
            'product_quantity': """Số lượng của sản phẩm/mặt hàng.""",
            'product_unit_price': """Giá tiền của 1 đơn vị sản phẩm/mặt hàng.""",
            'product_total_money': """Tổng tiền của sản phẩm/mặt hàng, tính bằng số lượng sản phẩm/mặt hàng nhân với giá tiền một đơn vị sản phẩm/mặt hàng."""
        }

    
    @staticmethod
    def get_instance(common_config, model_config):
        if LLMInformationExtractor.instance is None:
            LLMInformationExtractor.instance = LLMInformationExtractor(common_config, model_config)
        return LLMInformationExtractor.instance


    def get_prompt_system(self):
        # get json schema
        prompt = dict()
        for field in self.general_fields.keys():
            prompt[field] = (str, Field(description=self.general_fields[field]))
        object = dict()
        for sub_field in self.product_fields.keys():
            object[sub_field] = (str, Field(description=self.product_fields[sub_field]))
        Object = create_model("product", **{k: v for k, v in object.items()})
        prompt['products'] = (list[Object], Field(description="""Thông tin của các sản phẩm/mặt hàng có trong hoá đơn, theo thứ tự từ trên xuống dưới."""))
        Prompt = create_model("Receipt", **{k: v for k, v in prompt.items()})
        context = """Bạn là một hệ thống AI đẳng cấp thế giới hỗ trợ trích xuất NGUYÊN VẸN các thông tin từ một hoá đơn. Trả về kết quả theo định dạng json bằng tiếng Việt theo schema sau: {}""".format(Prompt.model_json_schema())
        return context


    def get_prompt(self, doc_data):
        messages = [
            {"role": "system", "content": self.get_prompt_system()},
            {"role": "user", "content": "Cho thông tin của một hoá đơn sau: {}, hãy trích xuất các thông tin cần thiết:".format(doc_data)},
        ]
        return messages


    @total_time
    def predict(self, request_id, inp, out, metadata):
        result = inp.get_data()
        doc_data = []
        for page_index in range(len(result['pages'])):
            doc_data.append(result['pages'][page_index]['text'])
        doc_data = '\n'.join(doc_data)
        result['doc_data'] = doc_data
        # import unidecode
        # doc_data = unidecode.unidecode(doc_data)

        messages = self.get_prompt(doc_data)
            
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        start = datetime.now()
        chat_response = self.client.completions.create(
            max_tokens=self.model_config['max_tokens'], 
            temperature=self.model_config['temperature'], 
            top_p=self.model_config['top_p'],
            model=self.model_config['lora_name'],
            echo=False,
            prompt=text
        )
        output_text = chat_response.choices[0].text
        result['raw_result'] = output_text
        metadata = self.add_metadata(metadata, 1, 1)
        out.set_data(result)
        return out, metadata