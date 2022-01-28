class ApiKey:

    def __init__(self, key_id, key):
        self.__key_id = key_id
        self.__key = key

    def format(self, format_str):
        return format_str.format(**self.as_dict())

    def as_dict(self):
        return {
            "key_id": self.__key_id,
            "key": self.__key
        }
