from .Models.Call import Call


class CallHistory:

    def __init__(self, request):
        self.__request = request

    def get(self, **kwargs):
        return self.create_collection(self.__request.post(
            '/{domain}/mongo_history/search.json',
            body=kwargs
        ))

    def create_collection(self, response):
        return [Call.from_dict(a) for a in response['data']]
