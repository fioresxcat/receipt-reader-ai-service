from inpout import *

class BaseMethod(object):
    def __init__(self, root_logger, time_logger, debugger):
        self.root_logger = root_logger
        self.time_logger = time_logger
        self.debugger = debugger
        
    
    def predict(self, request_id, inp):
        metadata = {}
        inp_data = inp.get_data()
        inp.set_data(inp_data)
        
        for module in self.modules:
            out = Output()
            if module.__class__.__name__ not in metadata.keys():
                metadata[module.__class__.__name__] = {
                    'num_request': 0,
                    'total_batch_size': 0
                }
            out, metadata = module.predict(request_id, inp, out, metadata)
            # end whole process if 1 module gets error or force quit=true and hit rule check
            if out.error != 0:
                if self.debugger is not None:
                    try:
                        self.debugger.log_module(str(request_id), inp, out, module.__class__.__name__)
                    except:
                        # raise
                        pass
                break
            else:
                # log module info to debug_dir if debugger is not None
                if self.debugger is not None:
                    try:
                        self.debugger.log_module(str(request_id), inp, out, module.__class__.__name__)
                    except:
                        # raise
                        pass
                inp.set_data(out.get_data())
        return out, metadata