import json 
import requests
import math
from .Report import Report
from .Metrica import Metrica

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

        base_url = "https://mazdata.ru/deltasales/get-leads-by-filter"

        request_base_params = {
            'auth_key': 'oweiurghw85gh74o8m7h48'
        }

        request_closed_leads_params = {
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
                    {"status_id": 142, "pipeline_id": 3346951},
                ]
            })
        }

        request_audits_leads_params = {
            "filter": json.dumps({
                "responsible_user_id": employee.amocrm_id,
                'custom_fields': {
                    '489154': {
                        "from": timestamp_from,
                        "to": timestamp_to
                    }
                }
            })
        }

        res = requests.get(base_url, params={
            **request_base_params,
            **request_closed_leads_params
        })

        audits_leads_res = requests.get(base_url, params={
            **request_base_params,
            **request_audits_leads_params
        })

        report = Report()

        report.add_metrica(Metrica("Кол-во исходящих звонков", len(res_outbound), 'calls'))
        report.add_metrica(Metrica("Кол-во входящих звонков", len(res_inbound), 'calls'))
        report.add_metrica(Metrica("Кол-во звонков всего", len(res_inbound) + len(res_outbound), 'calls'))
        report.add_metrica(Metrica("Денег за звонки", int((len(res_outbound) + len(res_inbound)) * employee.one_call_cost), 'calls', label='calls_money'))

        report.add_metrics(self.get_metrics_from_leads(res.json()['leads'], 1212574, "licenses", 'лицензий', 'лицензии', employee, lambda x: x/2))
        report.add_metrics(self.get_metrics_from_leads(res.json()['leads'], 1693720, "widgets", 'Виджетов', 'виджеты', employee))
        report.add_metrics(self.get_metrics_from_leads(res.json()['leads'], [1693621, 3346951], "projects", 'Проектов', 'проекты', employee))
        report.add_metrics(self.get_metrics_from_leads(res.json()['leads'], 3941655, "courses", 'Курсов', 'курсы', employee))

        report.add_metrica(Metrica("Аудитов продано", len(audits_leads_res.json()['leads']), 'audits'))
        report.add_metrica(Metrica("Денег за аудиты", 500 * len(audits_leads_res.json()['leads']), 'audits', label='audits_money'))

        money_amount = sum([
            report.get_metrica_by_label('calls_money').value,
            report.get_metrica_by_label('widgets_money').value,
            report.get_metrica_by_label('licenses_money').value,
            report.get_metrica_by_label('projects_money').value,
            report.get_metrica_by_label('courses_money').value,
            report.get_metrica_by_label('audits_money').value
        ])

        report.add_metrica(Metrica("Денег всего", money_amount))

        return report

    def get_metrics_from_leads(
        self,
        leads_list,
        pipeline_id_list,
        group,
        entity_name,
        entity_name_plural,
        employee,
        lead_price_processor = lambda x: x):

            if not isinstance(pipeline_id_list, list):
                pipeline_id_list = [pipeline_id_list]
                
            return [
                Metrica(entity_name + " продано", len([lead for lead in leads_list if lead['pipeline_id'] in pipeline_id_list]), group),
                Metrica(entity_name + " продано на сумму", sum([lead['price'] for lead in leads_list if lead['pipeline_id'] in pipeline_id_list]), group),
                Metrica("Денег за " + entity_name_plural, math.floor(sum([lead_price_processor(lead['price'])*(employee.sale_fee_percent/100) for lead in leads_list if lead['pipeline_id'] in pipeline_id_list])), group, label=group+"_money") 
            ]
