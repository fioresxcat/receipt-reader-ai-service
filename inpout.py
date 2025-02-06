class Input(object):
    def __init__(self, data={}):
        self.data = data 


    def set_data(self, data: dict) -> None:
        self.data = data


    def get_data(self) -> dict:
        return self.data 



class Output:
    def __init__(self, error_code=0, data={}):
        self.error = error_code
        self.data = data

    
    def set_error(self, error_code: int) -> None:
        self.error = error_code

    def set_data(self, data: dict) -> None:
        self.data = data 


    def get_data(self) -> dict:
        return self.data 


    def get_error(self) -> (dict):
        return self.error


