from methods.base_method import BaseMethod
from .text_detection import TextDetector
from .ocr import OCR
from .document_generation import DocumentGenerator
from .information_extraction.information_extraction_new import LLMInformationExtractor
from .postprocess import LLMPostprocessor


class OCRLLMProcessor(BaseMethod):
    def __init__(self, root_logger, time_logger, debugger, common_config, model_config):
        super(OCRLLMProcessor, self).__init__(root_logger, time_logger, debugger)
        self.triton_config = common_config['inference_server']
        self.vllm_config = common_config['vllm_server']
        self.model_config = model_config
        self.modules = [
            TextDetector.get_instance(self.triton_config, model_config['triton_models']['text_detection']),
            OCR.get_instance(self.triton_config, model_config['triton_models']),
            DocumentGenerator.get_instance(self.triton_config, model_config['triton_models']),
            LLMInformationExtractor.get_instance(self.vllm_config, model_config['vllm_models']['receipt-lora']),
            LLMPostprocessor.get_instance(self.triton_config, model_config)
        ]

