class Call:
    def __init__(self):
        self.uuid = None
        self.caller_id_name = None
        self.caller_id_number = None
        self.destination_number = None
        self.from_host = None
        self.to_host = None
        self.start_stamp = None
        self.end_stamp = None
        self.duration = None
        self.user_talk_time = None
        self.hangup_cause = None
        self.accountcode = None
        self.gateway = None

    @staticmethod
    def from_dict(dict_o):
        o = Call()
        o.__dict__.update(dict_o)
        return o
