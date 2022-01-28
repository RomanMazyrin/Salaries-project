from .OnpbxApiException import OnpbxApiException


class OnpbxApiAuthException(OnpbxApiException):

    def __init__(self, message):
        super().__init__(message)
