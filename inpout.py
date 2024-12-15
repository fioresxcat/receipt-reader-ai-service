class Input(object):
    def __init__(self, data={}):
        self.data = data 


    def set_data(self, data: dict) -> None:
        self.data = data


    def get_data(self) -> dict:
        return self.data 



class Output:
    def __init__(self, error_code=0, error_message='', data={}):
        self.error = {
            'error_code': 0,
            'error_msg': 'OK'
        }
        self.data = data

    
    def set_error(self, error_code: int, error_message: str) -> None:
        self.error['error_code'] = error_code 
        self.error['error_msg'] = error_message


    def set_data(self, data: dict) -> None:
        self.data = data 


    def get_data(self) -> dict:
        return self.data 


    def get_error(self) -> (dict):
        return self.error


