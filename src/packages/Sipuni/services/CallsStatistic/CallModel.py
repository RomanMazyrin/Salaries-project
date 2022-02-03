class CallModel:
    def __init__(self):
        self.type = None
        self.status = None
        self.call_time = None
        self.call_schema_id = None
        self.schema = None
        self.outbound_line = None
        self.call_from = None
        self.call_to = None
        self.answered_user_id = None
        self.call_duration = None
        self.talk_duration = None
        self.answer_time = None
        self.score = None
        self.record_id = None
        self.mark = None
        self.tags = None
        self.call_order_id = None
        self.is_record_exists = None
        self.is_new_client = None
        self.dtmf = None
        self.callback_state = None
        self.callback_time = None
        self.crm_info = None
        self.crm_responsible_user = None

    @staticmethod
    def from_dict(dict_o):
        call = CallModel()
        call.__dict__.update(dict_o)
        return call
