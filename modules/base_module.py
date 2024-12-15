'''
    bắt 2 exception:
    - timeout
    - tritonserver internal error
'''

import pdb
import grpc
import logging
import numpy as np
import tritonclient.grpc as grpcclient

from utils import total_time

class BaseModule(object):
    def __init__(self, common_config, model_config):
        self.model_config = model_config
        self.common_config = common_config
        self.max_request_time = int(self.common_config['MAX_RETRY'])
        self.root_logger = logging.getLogger('root')
        self.time_logger = logging.getLogger('time')
        if int(self.common_config['USE_SSL']) == 0:
            self.triton_client = grpcclient.InferenceServerClient(url=self.common_config['ip'] + ':' + self.common_config['port'], ssl=False)
        else:
            self.triton_client = grpcclient.InferenceServerClient(url=self.common_config['ip'] + ':' + self.common_config['port'], ssl=True)
        
        
    def add_metadata(self, metadata, num_request, batch_size):
        metadata[self.__class__.__name__]['num_request'] += num_request
        metadata[self.__class__.__name__]['total_batch_size'] += batch_size
        return metadata
        
        
    def request(self, data):
        if type(data) != np.ndarray:
            data = data.numpy()
        data_shape = list(data.shape)
        infer_inputs = []
        infer_outputs = []
        infer_inputs.append(grpcclient.InferInput(self.model_config['input_name'], [data_shape[0], data_shape[1], data_shape[2], data_shape[3]], self.model_config['input_type']))
        if isinstance(self.model_config['output_name'], list):
            for output_name in self.model_config['output_name']:
                infer_outputs.append(grpcclient.InferRequestedOutput(output_name))
        else:
            infer_outputs.append(grpcclient.InferRequestedOutput(self.model_config['output_name']))
        infer_inputs[0].set_data_from_numpy(data)
        # request to triton server
        num_request = 0
        while num_request < self.max_request_time:
            try:
                num_request += 1
                results = self.triton_client.infer(model_name=self.model_config['model_spec_name'], inputs=infer_inputs, outputs=infer_outputs)
                break
            except:
                if num_request == self.max_request_time:
                    raise
                else:
                    continue
        return results

    
    def request_multi(self, data):
        infer_inputs = []
        infer_outputs = []
        for i, input_data in enumerate(data):
            if type(input_data) != np.ndarray:
                input_data = input_data.numpy()
            data_shape = list(input_data.shape)
            infer_inputs.append(grpcclient.InferInput(self.model_config['input_name'][i], data_shape, self.model_config['input_type'][i]))
            infer_inputs[i].set_data_from_numpy(input_data)
        if isinstance(self.model_config['output_name'], list):
            for output_name in self.model_config['output_name']:
                infer_outputs.append(grpcclient.InferRequestedOutput(output_name))
        else:
            infer_outputs.append(grpcclient.InferRequestedOutput(self.model_config['output_name']))
        # request to triton server
        num_request = 0
        while num_request < self.max_request_time:
            try:
                num_request += 1
                results = self.triton_client.infer(model_name=self.model_config['model_spec_name'], inputs=infer_inputs, outputs=infer_outputs)
                break
            except:
                if num_request == self.max_request_time:
                    raise
                else:
                    continue
        return results


    def request_seq(self, data):
        if type(data) != np.ndarray:
            data = data.numpy()
        data_shape = list(data.shape)
        infer_inputs = []
        infer_outputs = []
        infer_inputs.append(grpcclient.InferInput(self.model_config['input_name'], [data_shape[0], data_shape[1], data_shape[2], data_shape[3], data_shape[4]], self.model_config['input_type']))
        if isinstance(self.model_config['output_name'], list):
            for output_name in self.model_config['output_name']:
                infer_outputs.append(grpcclient.InferRequestedOutput(output_name))
        else:
            infer_outputs.append(grpcclient.InferRequestedOutput(self.model_config['output_name']))
        infer_inputs[0].set_data_from_numpy(data)
        # request to triton server
        num_request = 0
        while num_request < self.max_request_time:
            try:
                num_request += 1
                results = self.triton_client.infer(model_name=self.model_config['model_spec_name'], inputs=infer_inputs, outputs=infer_outputs)
                break
            except:
                if num_request == self.max_request_time:
                    raise
                else:
                    continue
        return results
    
    
    def predict(self, request_id, info, metadata, *args, **kwargs):
        pass


