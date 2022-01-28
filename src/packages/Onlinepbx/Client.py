from .CallHistory import CallHistory
from .OnpbxApiRequest import OnpbxApiRequest


class Client:
    """ Client for Onlinepbx API """

    services_map = {
        'call_history': CallHistory
    }

    def __init__(self, subdomain, api_key):
        self.__subdomain = subdomain
        self.__api_key = api_key
        self.__on_key_refresh = None
        self.__key = None

    def on_key_refresh(self, callback):
        self.__on_key_refresh = callback

    def set_key(self, key):
        self.__key = key

    def __getattr__(self, item):
        return self.services_map[item](
            OnpbxApiRequest(self.__subdomain, self.__api_key, self.__key)
        )
