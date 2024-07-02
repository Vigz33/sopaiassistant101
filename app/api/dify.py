# Author: Shomu Maitra
# Email: s.maitra@maersk.com
# Description: Dify apis
# Date: 27th March 2024

import config
import api.crud as crud
import json
from urllib.parse import urlencode

# Dify
class DifyApi:

    base_url: str
    api_key: str
    def __init__(self, base_url, api_key):
        self.base_url=base_url
        self.api_key=api_key
 
    # Create
    def getKey(self): 
        if self.api_key != None :
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Content-Type': 'application/json'
            }
            return headers
        else:
            raise ValueError("Check Authorization key!")

    # Create
    def create(self, payload):
        try:
            url = str(self.base_url)
            headers = self.getKey()
            payload = json.dumps(payload, default=lambda obj: obj.__dict__)
            
            print("Calling URL: ", url, " Payload to Dify: ", payload)
            responce = crud.create(url, headers, payload)
            return responce
        except Exception as e:
            print('Error ', e)