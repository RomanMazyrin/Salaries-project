import csv
from io import StringIO

from .services.CallsStatistic.CallModel import CallModel

FIELDS_MAP = {
    "Тип": "type",
    "Статус": "status",
    "Время": "call_time",
    "ID схемы звонка": "call_schema_id",
    "Схема": "schema",
    "Исходящая линия": "outbound_line",
    "Откуда": "call_from",
    "Куда": "call_to",
    "Кто ответил": "answered_user_id",
    "Длительность звонка": "call_duration",
    "Длительность разговора": "talk_duration",
    "Время ответа": "answer_time",
    "Оценка": "score",
    "ID записи": "record_id",
    "Метка": "mark",
    "Теги": "tags",
    "ID заказа звонка": "call_order_id",
    "Запись существует": "is_record_exists",
    "Новый клиент": "is_new_client",
    "Dtmf": "dtmf",
    "Состояние перезвона": "callback_state",
    "Время перезвона": "callback_time",
    "Информация из CRM": "crm_info",
    "Ответственный из CRM": "crm_responsible_user",
}


def parse_calls(csv_str):
    csv_str_io = StringIO(csv_str)
    reader = csv.DictReader(csv_str_io, delimiter=";")
    calls = []
    for raw in reader:
        call_params_dict = dict(
            (FIELDS_MAP[key], value) for (key, value) in raw.items() if FIELDS_MAP.get(key)
        )
        call = CallModel.from_dict(call_params_dict)
        calls.append(call)
    return calls
