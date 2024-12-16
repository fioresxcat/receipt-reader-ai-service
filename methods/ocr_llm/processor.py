from methods.base_method import BaseMethod
from .text_detection import TextDetector
from .ocr import OCR
from .document_generation import DocumentGenerator
from .information_extraction import InformationExtractor
from .postprocess import Postprocessor


class OCRLLMProcessor(BaseMethod):
    def __init__(self, root_logger, time_logger, debugger, triton_config, vllm_config, model_config):
        super(OCRLLMProcessor, self).__init__(root_logger, time_logger, debugger)
        self.triton_config = triton_config
        self.model_config = model_config
        self.modules = [
            TextDetector.get_instance(triton_config, model_config['triton_models']['text_detection']),
            OCR.get_instance(triton_config, model_config['triton_models']),
            DocumentGenerator.get_instance(triton_config, model_config['triton_models']),
            InformationExtractor.get_instance(vllm_config, model_config['vllm_models']['base-model']),
            Postprocessor.get_instance(triton_config, model_config)
        ]

