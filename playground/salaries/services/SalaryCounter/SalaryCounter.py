import json 
import requests

class SalaryCounter:

    def __init__(self, onpbx_client=None):
        self.__onpbx_client = onpbx_client

    def get_detailed_report(self, employee, timestamp_from, timestamp_to):
        res_outbound = self.__onpbx_client.call_history.get(
            accountcode='outbound',
            caller_id_number=str(employee.onpbx_id),
            start_stamp_from=int(timestamp_from),
            start_stamp_to=int(timestamp_to),
            duration_from=21
        )

        res_inbound = self.__onpbx_client.call_history.get(
            accountcode='inbound',
            destination_number=str(employee.onpbx_id),
            start_stamp_from=int(timestamp_from),
            start_stamp_to=int(timestamp_to),
            user_talk_time_from=21
        )

        request_params = {
            'auth_key': 'oweiurghw85gh74o8m7h48',
            "filter": json.dumps({
                "closed_at": {
                    "from": timestamp_from,
                    "to": timestamp_to
                },
                "responsible_user_id": employee.amocrm_id,
                "statuses": [
                    {"status_id": 142, "pipeline_id": 1212574},
                    {"status_id": 142, "pipeline_id": 1693621},
                    {"status_id": 142, "pipeline_id": 1693720},
                    {"status_id": 142, "pipeline_id": 3941655},
                ]
            })
        }

        res = requests.get("https://mazdata.ru/deltasales/get-leads-by-filter", params=request_params)

        report_obj = {

            'calls_outbound_count': len(res_outbound),
            'calls_inbound_count': len(res_inbound),
            'calls_total_count': len(res_inbound) + len(res_outbound),
            'money_for_calls': int((len(res_outbound) + len(res_inbound)) * employee.one_call_cost),

            'licenses_amount': len([lead for lead in res.json()['leads'] if lead['pipeline_id'] == 1212574]),
            'licenses_sum': sum([lead['price'] for lead in res.json()['leads'] if lead['pipeline_id'] == 1212574]),
            'money_for_licenses': sum([(lead['price']/2)*(employee.sale_fee_percent/100) for lead in res.json()['leads'] if lead['pipeline_id'] == 1212574]),

            'widgets_amount': len([lead for lead in res.json()['leads'] if lead['pipeline_id'] == 1693720]),
            'widgets_sum': sum([lead['price'] for lead in res.json()['leads'] if lead['pipeline_id'] == 1693720]),
            'money_for_widgets': sum([lead['price']*(employee.sale_fee_percent/100) for lead in res.json()['leads'] if lead['pipeline_id'] == 1693720]),

            'projects_amount': len([lead for lead in res.json()['leads'] if lead['pipeline_id'] == 1693621]),
            'projects_sum': sum([lead['price'] for lead in res.json()['leads'] if lead['pipeline_id'] == 1693621]),
            'money_for_projects': sum([lead['price']*(employee.sale_fee_percent/100) for lead in res.json()['leads'] if lead['pipeline_id'] == 1693621]),


            'courses_amount': len([lead for lead in res.json()['leads'] if lead['pipeline_id'] == 3941655]),
            'courses_sum': sum([lead['price'] for lead in res.json()['leads'] if lead['pipeline_id'] == 3941655]),
            'money_for_courses': sum([lead['price']*(employee.sale_fee_percent/100) for lead in res.json()['leads'] if lead['pipeline_id'] == 3941655])
        
        }

        report_obj['money'] = sum([
            report_obj['money_for_calls'],
            report_obj['money_for_licenses'],
            report_obj['money_for_widgets'],
            report_obj['money_for_projects'],
            report_obj['money_for_courses']
        ])

        return report_obj
