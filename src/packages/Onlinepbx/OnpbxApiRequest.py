import requests

from .AuthClient import AuthClient
from .Constants import BASE_URL
from .Exceptions.OnpbxApiAuthException import OnpbxApiAuthException
from .Exceptions.OnpbxApiException import OnpbxApiException


class OnpbxApiRequest:
    def __init__(self, subdomain, api_key, key):
        self.__subdomain = subdomain
        self.__key = key
        self.__api_key = api_key

    def refresh_key(self):
        auth_client = AuthClient(self.__subdomain, self.__api_key)
        self.__key = auth_client.get_auth_key("true")

    def get_method_full_url(self, method):
        return BASE_URL + "/" + method.format(domain=self.__subdomain + ".onpbx.ru").strip("/")

    def post(self, method, body=None, headers=None, need_to_refresh=False):

        if headers is None:
            headers = {}
        if body is None:
            body = {}

        if need_to_refresh:
            self.refresh_key()

        key_header = self.get_api_key_header()
        if key_header is not None:
            headers.update(key_header)

        response = requests.post(self.get_method_full_url(method), headers=headers, data=body)
        try:
            parsed_response = self.parse_response(response)
            return parsed_response
        except OnpbxApiAuthException as e:
            if need_to_refresh:
                raise e
            return self.post(method, body, headers, True)

    def get_api_key_header(self):
        if not self.__key:
            return None
        header_name = "x-pbx-authentication"
        header_value_tmpl = "{key_id}:{key}"
        return {header_name: self.__key.format(header_value_tmpl)}

    def parse_response(self, response):
        try:
            parsed_response = response.json()
            if parsed_response.get("status") == "0":
                self.check_response_status(parsed_response)
            return parsed_response
        except ValueError:
            raise OnpbxApiException("Response is not valid JSON")

    def check_response_status(self, response):
        if response.get("isNotAuth"):
            raise OnpbxApiAuthException("Unauthorized")
