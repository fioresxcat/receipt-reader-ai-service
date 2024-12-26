import streamlit as st
import pandas as pd
import json
from PIL import Image
import cv2
import base64
import numpy as np

import os
import pdb
import json
import utils
import logging
import argparse
from pathlib import Path
import logging.config
logging.config.fileConfig('configs/logging.conf')

from datetime import datetime

from debugger import Debugger
from inpout import Input, Output
from methods import MethodProcessor


# load config
root_logger = logging.getLogger('root')
time_logger = logging.getLogger('time')
config_env = utils.load_yaml('configs/config_env.yaml')
config_methods = utils.load_yaml('configs/config_methods.yaml')
config_models = utils.load_yaml('configs/config_models.yaml')
config_common = utils.load_yaml('configs/config_common.yaml')
list_mart_types = ['coopmart', 'emart', 'gs25', 'newbigc_go_top', 'winmart_combined']

debugger = Debugger(log_path='logs/demo')
method_processors = MethodProcessor(config_env, config_methods, config_models, root_logger, time_logger, debugger)

def process_image(image, mart_type, flow):
    # convert mart_type
    mapping_dict = {
        'Emart': 'emart',
        'Winmart': 'vinmart',
        'Coopmart': 'coopmart',
        'GS25': 'gs25',
        'BIGC': 'new_bigc'
    }
    mart_type = mapping_dict[mart_type]
    images = [image]
    # gen request
    inp = Input(data = {'rotated_images': images, 'mart_type': mart_type})
    if flow == 'Normal OCR':
        out, metadata = method_processors.methods['OCR'].predict('file1', inp)
    elif flow == 'LLM OCR':
        out, metadata = method_processors.methods['OCR_LLM'].predict('file1', inp)

    if flow == 'Normal OCR':
        out_data = out.get_data()['result']
        return out_data
    else:
        out_data = out.get_data()
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
        return result


# Streamlit UI title
st.title("Receipt Information Extractor")

# Section to upload an image
uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"])

# Selection of mart type
mart_type = st.selectbox(
    "Select the mart type of the receipt",
    ["Emart", "Winmart", "Coopmart", "GS25", "BIGC"]
)

# Selection for model choice
model_choice = st.selectbox(
    "Select the model to use for processing",
    ["Normal OCR", "LLM OCR"]
)

# Submit button to process the image
if st.button("Submit"):
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        base64_string = base64.b64encode(bytes_data)
        nparr = np.frombuffer(base64.b64decode(base64_string), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Uploaded Receipt Image", use_container_width=True)

        # Placeholder for model processing (user-defined)
        st.info("Processing the image...")
        
        # Get the result from the simulated processing function
        result = process_image(image, mart_type, model_choice)
        
        # Display the result as JSON
        st.subheader("Extracted Information")
        st.json(result)
        
        # # Display extracted fields as a table (if "Items" field exists)
        # if "Items" in result:
        #     items_df = pd.DataFrame(result["Items"])
        #     st.subheader("Items Table")
        #     st.table(items_df)
    else:
        st.error("Please upload an image before submitting.")
