import pdb
from .app_check.processor import AppCheckProcessor
from .ocr.processor import OCRProcessor
from .ocr_llm.processor import OCRLLMProcessor

class MethodProcessor(object):
    def __init__(self, config_env, config_methods, config_models, root_logger, time_logger, debugger=None):
        self.config_env = config_env
        self.config_methods = config_methods
        self.config_models = config_models
        self.root_logger = root_logger
        self.time_logger = time_logger
        self.debugger = debugger
        self.method_mapper = {
            'OCR': OCRProcessor,
            'OCR_LLM': OCRLLMProcessor,
            'AppCheck': AppCheckProcessor
        }
        self.init_methods()


    def init_methods(self):
        self.methods = {}
        for method_name in self.config_methods['use_methods'].keys():
            if self.config_methods['use_methods'][method_name]:
                self.methods[method_name] = self.method_mapper[method_name](self.root_logger, self.time_logger, self.debugger, self.config_env, self.config_models)