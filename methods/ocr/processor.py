from methods.base_method import BaseMethod
from .text_detection import TextDetector
from .ocr import OCR
from .information_extraction import InformationExtractor
from .postprocess import PostProcessor

class OCRProcessor(BaseMethod):
    def __init__(self, root_logger, time_logger, debugger, common_config, model_config, force_quit):
        super(OCRProcessor, self).__init__(root_logger, time_logger, debugger)
        self.common_config = common_config
        self.model_config = model_config
        self.force_quit = 0
        self.modules = [
            TextDetector.get_instance(common_config, model_config['triton_models']['text_detection']),
            OCR.get_instance(common_config, model_config['triton_models']),
            InformationExtractor.get_instance(common_config, model_config['triton_models']['receipt_information_extraction']),
            PostProcessor.get_instance(common_config, model_config['triton_models']),
        ]