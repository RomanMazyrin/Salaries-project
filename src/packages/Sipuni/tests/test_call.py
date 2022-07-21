from packages.Sipuni.services.CallsStatistic.CallModel import CallModel


def test_call_model_creation_from_dict():
    call = CallModel.from_dict(
        {
            "type": "1",
            "status": "2",
            "call_time": "3",
            "call_schema_id": "4",
            "schema": "5",
            "outbound_line": "6",
            "call_from": "7",
            "call_to": "8",
            "answered_user_id": "9",
            "call_duration": "10",
            "talk_duration": "11",
            "answer_time": "12",
            "score": "13",
            "record_id": "14",
            "mark": "15",
            "tags": "16",
            "call_order_id": "17",
            "is_record_exists": "18",
            "is_new_client": "19",
            "dtmf": "20",
            "callback_state": "21",
            "callback_time": "22",
            "crm_info": "23",
            "crm_responsible_user": "24",
        }
    )

    assert call.type == "1"
    assert call.status == "2"
    assert call.call_time == "3"
    assert call.call_schema_id == "4"
    assert call.schema == "5"
    assert call.outbound_line == "6"
    assert call.call_from == "7"
    assert call.call_to == "8"
    assert call.answered_user_id == "9"
    assert call.call_duration == "10"
    assert call.talk_duration == "11"
    assert call.answer_time == "12"
    assert call.score == "13"
    assert call.record_id == "14"
    assert call.mark == "15"
    assert call.tags == "16"
    assert call.call_order_id == "17"
    assert call.is_record_exists == "18"
    assert call.is_new_client == "19"
    assert call.dtmf == "20"
    assert call.callback_state == "21"
    assert call.callback_time == "22"
    assert call.crm_info == "23"
    assert call.crm_responsible_user == "24"
