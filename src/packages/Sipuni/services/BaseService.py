import hashlib

from ..Constants import BASE_API_URL


class BaseService:

    SERVICE_URL_NAME = None

    def __init__(self, user_id, secret):
        self._user_id = user_id
        self._secret = secret

    @staticmethod
    def _make_hash(*args):
        stringForHash = "+".join(args)
        return hashlib.md5(stringForHash.encode()).hexdigest()

    @classmethod
    def get_service_method_api_url(clss, method):
        return BASE_API_URL + "/" + clss.SERVICE_URL_NAME + "/" + method
