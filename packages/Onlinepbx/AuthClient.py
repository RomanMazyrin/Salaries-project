import requests

from .ApiKey import ApiKey
from .Constants import BASE_URL


class AuthClient:

    def __init__(self, subdomain, api_key):
        self.__subdomain = subdomain
        self.__api_key = api_key

    def get_method_full_url(self, method):
        return BASE_URL + "/" + method.format(domain=self.__subdomain + ".onpbx.ru").strip("/")

    def get_auth_key(self, new="false"):
        auth_url = self.get_method_full_url('/{domain}/auth.json')
        response = requests.post(auth_url, data={
            "auth_key": self.__api_key,
            "new": new
        })
        key = self.parse_response(response)
        return key

    def parse_response(self, response):
        if response.status_code == 200:
            response_body = response.json()
            status = response_body['status']
            if str(status) == "1":
                return ApiKey(response_body['data']["key_id"], response_body['data']["key"])
            else:
                return None
        else:
            raise Exception("Response code is %s" % response.status_code)