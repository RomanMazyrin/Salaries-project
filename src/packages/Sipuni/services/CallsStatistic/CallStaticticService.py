import requests
from packages.Sipuni.CsvParser import parse_calls
from packages.Sipuni.services.BaseService import BaseService


class CallStatisticService(BaseService):

    SERVICE_URL_NAME = 'statistic'

    def get(self, anonymous='', dtmf_user_answer='', first_time='', from_date='', from_number='',
            numbers_ringed='', outgoing_line='', show_tree_id='', state='', to_date='',
            to_answer='', to_number='', tree='', call_type=''):

        hashString = self._make_hash(
            anonymous,
            dtmf_user_answer,
            first_time,
            from_date,
            from_number,
            numbers_ringed,
            outgoing_line,
            show_tree_id,
            state,
            to_date,
            to_answer,
            to_number,
            tree,
            call_type,
            self._user_id,
            self._secret
        )

        query = {
            'anonymous': anonymous,
            'firstTime': first_time,
            'from': from_date,
            'fromNumber': from_number,
            'numbersRinged': numbers_ringed,
            'outgoingLine': outgoing_line,
            'showTreeId': show_tree_id,
            'state': state,
            'to': to_date,
            'toAnswer': to_answer,
            'toNumber': to_number,
            'tree': tree,
            'type': call_type,
            'user': self._user_id,
            'dtmfUserAnswer': dtmf_user_answer,
            'hash': hashString
        }

        response = requests.get(self.get_service_method_api_url('export'), params=query)

        if response.status_code != 200:
            return []

        calls = parse_calls(response.text)
        return calls
