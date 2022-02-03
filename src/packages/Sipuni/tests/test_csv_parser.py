from packages.Sipuni.CsvParser import parse_calls
from packages.Sipuni.services.CallsStatistic.CallModel import CallModel


def test_parser(calls_csv_str):

    calls_list = parse_calls(calls_csv_str)
    first_call = calls_list[0]

    assert type(first_call) == CallModel
    assert first_call.type == 'Исходящий'
    assert first_call.crm_info == 'Firstname secondname'
    assert first_call.call_time == '27.03.2019 11:12:53'
