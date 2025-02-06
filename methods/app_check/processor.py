from methods.base_method import BaseMethod
from .app_check import AppCheck

class AppCheckProcessor(BaseMethod):
    def __init__(self, root_logger, time_logger, debugger, common_config, model_config):
        super(AppCheckProcessor, self).__init__(root_logger, time_logger, debugger)
        self.triton_config = common_config['inference_server']
        triton_config = self.triton_config
        self.model_config = model_config
        self.force_quit = 0
        self.modules = [
            AppCheck.get_instance(triton_config, model_config),
        ]