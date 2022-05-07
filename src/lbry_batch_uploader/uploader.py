import requests


class Uploader:
    def __init__(self):
        pass

    def upload_thumbnail(self, thumbnail_params) -> dict:
        """Helper function for uploading thumbnail to spee.ch"""
        req_result = requests.post(
            "https://spee.ch/api/claim/publish",
            data=thumbnail_params
        )  
        return self._check_response(req_result)
    
    def upload_file_to_lbry(self, file_params) -> dict:
        """Helper function for uploading file to LBRY"""
        req_result = requests.post(
            "http://localhost:5279/",
            data=file_params
        )    
        return self._check_response(req_result)

    def _check_response(self, req_result, *, error_json=None) -> dict:
        """Helper function for checking response from api"""
        status = req_result.status_code
        
        if error_json is None:
            error_json = {'Error': status}

        return req_result.json() if status == 200 else error_json


if __name__ == '__main__':
    pass
