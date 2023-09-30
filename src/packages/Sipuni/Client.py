from .services.CallsStatistic.CallStaticticService import CallStatisticService


class Client:
    services_map = {"calls_stats": CallStatisticService}

    def __init__(self, user_id, secret_key):
        self.__user_id = user_id
        self.__secret_key = secret_key

    def __getattr__(self, item):
        return self.services_map[item](self.__user_id, self.__secret_key)

    @property
    def calls_stats(self):
        return self.services_map["calls_stats"](self.__user_id, self.__secret_key)
