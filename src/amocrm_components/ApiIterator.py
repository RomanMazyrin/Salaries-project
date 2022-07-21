import json
import requests
import time


class ApiIterator:
    def __init__(
        self,
        url,
        fetch_limit=50,
        start_page=1,
        params={},
        entity_type="",
        total_limit=None,
        request_pause_timeout=1,
    ):

        self.url = url
        self.limit = fetch_limit
        self.start_page = start_page
        self.params = params
        self.entity_type = entity_type
        self.total_limit = total_limit
        self.request_pause_timeout = request_pause_timeout

    def get_next(self):
        page = self.start_page
        count = 0

        while True:
            batch = self.__fetch_batch(page)

            for entity in batch:
                count += 1
                yield entity
                if self.total_limit == count:
                    return

            if self.request_pause_timeout:
                time.sleep(self.request_pause_timeout)

            page += 1

            if (len(batch) < self.limit) or len(batch) == 0:
                return

    def __fetch_batch(self, page):
        request_params = self.__get_request_params_with_page_and_limit(page)
        res = requests.get(self.url, params=request_params)
        entities = res.json()[self.entity_type]
        return entities

    def __get_request_params_with_page_and_limit(self, page):
        limit_params = {"limit": self.limit, "page": page}

        request_params = self.params.copy()

        if "filter" in request_params:
            filter_params = request_params["filter"]
            if type(filter_params) == str:
                filter_params = json.loads(filter_params)
        else:
            filter_params = {}

        filter_params.update(limit_params)
        request_params["filter"] = json.dumps(filter_params)
        return request_params
