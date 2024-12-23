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

from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any, List


class ProductInfo(BaseModel):
    product_name: str = Field(description="""Tên của sản phẩm/mặt hàng.""")
    product_id: str = Field(description="""Mã SKU của sản phẩm/mặt hàng.""")
    product_quantity: str = Field(description="""Số lượng của sản phẩm/mặt hàng.""")
    product_unit_price: str = Field(description="""Giá tiền của 1 đơn vị sản phẩm/mặt hàng.""")
    product_total_money: str = Field(description="""Tổng tiền của sản phẩm/mặt hàng, tính bằng số lượng sản phẩm/mặt hàng nhân với giá tiền một đơn vị sản phẩm/mặt hàng.""")
    

class BaseExtractInfo(BaseModel):
    mart_name : str = Field(description="""Tên của cửa hàng/Siêu thị phát hành hoá đơn này.""")
    # phone : list[str] = Field(description="""Số điện thoại của cửa hàng/Siêu thị phát hành hoá đơn, theo sau cụm từ \"Điện thoại\" hoặc \"SĐT\" hoặc tương tự.""")
    # address: str = Field(description="""Địa chỉ của cửa hàng/Siêu thị phát hành hóa đơn.""")
    # website: list[str] = Field(description="""Website của cửa hàng/Siêu thị phát hành hoá đơn.""")
    staff : str = Field(description="""Tên hoặc mã số của thu ngân/nhân viên in hoá đơn, theo sau từ \"thu ngân\" hoặc \"nhân viên\" hoặc tương tự.""")
    date : str = Field(description="""Ngày in hoá đơn, trả về theo định dạng dd/mm/yyyy.""")
    time : str = Field(description="""Thời gian theo hh:mm:ss in hoá đơn.""")
    receipt_id: str = Field(description="""Dãy số hoặc ký tự xác định hóa đơn, thường theo sau \"Số hoá đơn\" hoặc \"Số HĐ\" hoặc \"HĐ\" hoặc \"Số giao dịch\" hoặc \"Ticket\" hoặc tương tự.""")
    pos_id : str = Field(description="""Mã/Số của quầy in hoá đơn, thường được viết là Quầy, Pos.""")
    total_quantity : str = Field(description="""Tổng số lượng sản phẩm của hoá đơn.""")
    total_money : str = Field(description="""Tổng tiền của hoá đơn sau giảm giá/Số tiền mà khách hàng phải trả.""")
    # total_original_money : str = Field(description="""Tổng tiền của hoá đơn trước khi giảm giá/Tổng tiền của tất cả sản phẩm trong hoá đơn.""")
    # total_discount_money : str = Field(description="""Tổng số tiền được giảm giá/Tổng của số tiền giảm giá của từng sản phầm.""")
    product_info : list[ProductInfo] = Field(description="""Thông tin của các sản phẩm/mặt hàng có trong hoá đơn, theo thứ tự từ trên xuống dưới.""")


class InformationExtractor(BaseModuleVLLM):
    
    instance = None
    
    def __init__(self, common_config, model_config):
        super(InformationExtractor, self).__init__(common_config, model_config)
        self.my_dir = os.path.dirname(__file__)
        self.tokenizer = AutoTokenizer.from_pretrained(os.path.join(self.my_dir, self.model_config['base_model_name']))

    
    @staticmethod
    def get_instance(common_config, model_config):
        if InformationExtractor.instance is None:
            InformationExtractor.instance = InformationExtractor(common_config, model_config)
        return InformationExtractor.instance


    def get_prompt_system(self):
        base_schema = BaseExtractInfo.model_json_schema()
        context = """Bạn là một hệ thống AI đẳng cấp thế giới hỗ trợ trích xuất các thông tin từ một hoá đơn. Trả về kết quả theo định dạng json bằng tiếng Việt theo schema sau: {}""".format(base_schema)
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
        # pdb.set_trace()
        result['raw_result'] = output_text
        metadata = self.add_metadata(metadata, 1, 1)
        out.set_data(result)
        return out, metadata
