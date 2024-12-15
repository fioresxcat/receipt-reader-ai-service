from methods.base_method import BaseMethod
from .receipt_classification import ReceiptClassifier
from .text_detection import TextDetector
from .ocr import OCR
from .information_extraction import InformationExtractor
from .ocr_barcode import OCRBarcode
from .postprocess import PostProcessor
from .il001 import IL001
from .il002 import IL002
from .il003 import IL003
from .it001 import IT001
from .it002 import IT002
from .fr002 import FR002

class OCRProcessor(BaseMethod):
    def __init__(self, root_logger, time_logger, debugger, common_config, model_config, force_quit):
        super(OCRProcessor, self).__init__(root_logger, time_logger, debugger)
        self.common_config = common_config
        self.model_config = model_config
        self.force_quit = 0
        self.modules = [
            ReceiptClassifier.get_instance(common_config, model_config['receipt_classification']),
            TextDetector.get_instance(common_config, model_config['text_detection']),
            OCR.get_instance(common_config, model_config),
            InformationExtractor.get_instance(common_config, model_config),
            OCRBarcode.get_instance(common_config, model_config),
            PostProcessor.get_instance(common_config, model_config),
            IL001.get_instance(common_config, model_config),
            IL002.get_instance(common_config, model_config),
            IL003.get_instance(common_config, model_config),
            IT001.get_instance(common_config, model_config),
            IT002.get_instance(common_config, model_config),
            FR002.get_instance(common_config, model_config['fraud_hand_written_detection'])
        ]