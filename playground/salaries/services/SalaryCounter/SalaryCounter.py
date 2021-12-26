import json 
import requests
import math
from .Metrica import Metrica
from .Report import Report
from amocrm_components.ApiIterator import ApiIterator


class SalaryCounter:

    META_PARAM_COUNT_IN_TOTAL_SUM = 'COUNT_IN_TOTAL_SUM'

    def __init__(self, employee, onpbx_client):
        self.__employee = employee
        self.__onpbx_client = onpbx_client

    def __get_metrics_for_calls(self, timestamp_from, timestamp_to):
        
        metrics = []

        if not self.__employee.onpbx_id:
            return metrics

        res_outbound = self.__onpbx_client.call_history.get(
            accountcode='outbound',
            caller_id_number=str(self.__employee.onpbx_id),
            start_stamp_from=int(timestamp_from),
            start_stamp_to=int(timestamp_to),
            duration_from=self.__employee.min_call_length+1
        )

        res_inbound = self.__onpbx_client.call_history.get(
            accountcode='inbound',
            destination_number=str(self.__employee.onpbx_id),
            start_stamp_from=int(timestamp_from),
            start_stamp_to=int(timestamp_to),
            user_talk_time_from=self.__employee.min_call_length+1
        )

        metrics.append(Metrica("Кол-во исходящих звонков", len(res_outbound), 'calls'))
        metrics.append(Metrica("Кол-во входящих звонков", len(res_inbound), 'calls'))
        metrics.append(Metrica("Кол-во звонков всего", len(res_inbound) + len(res_outbound), 'calls'))

        metrics.append(Metrica(
            "Денег за звонки",
            int((len(res_outbound) + len(res_inbound)) * (self.__employee.one_call_cost if self.__employee.one_call_cost else 0)),
            group = 'calls',
            label = 'calls_money',
            meta_params = {self.META_PARAM_COUNT_IN_TOTAL_SUM: True}
        ))

        return metrics

    def __get_metrics_for_amo_leads(self, timestamp_from, timestamp_to):

        metrics = []

        if not self.__employee.amocrm_id:
            return metrics

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
                "responsible_user_id": self.__employee.amocrm_id,
                "statuses": [
                    {"status_id": 142, "pipeline_id": 1212574},
                    {"status_id": 142, "pipeline_id": 1693621},
                    {"status_id": 142, "pipeline_id": 1693720},
                    {"status_id": 142, "pipeline_id": 3941655},
                    {"status_id": 142, "pipeline_id": 3346951},
                    {"status_id": 142, "pipeline_id": 3964107},
                    {"status_id": 142, "pipeline_id": 3678177},
                    {"status_id": 142, "pipeline_id": 4669350}
                ]
            })
        }

        request_audits_leads_params = {
            "filter": json.dumps({
                "responsible_user_id": self.__employee.amocrm_id,
                'custom_fields': {
                    '489154': {
                        "from": timestamp_from,
                        "to": timestamp_to
                    }
                }
            })
        }

        request_projects_with_worktime = {
            "filter": json.dumps({
                "responsible_user_id": self.__employee.amocrm_id,
                "closed_at": {
                    "from": timestamp_from,
                    "to": timestamp_to
                },
                "statuses": [
                    {"status_id": 142, "pipeline_id": 3346951},
                ]
            })
        }

        res = requests.get(base_url, params={
            **request_base_params,
            **request_closed_leads_params
        })

        success_leads = res.json()['leads']

        audits_leads_res = requests.get(base_url, params={
            **request_base_params,
            **request_audits_leads_params
        })

        projects_worktime_leads = requests.get(base_url, params={
            **request_base_params,
            **request_projects_with_worktime
        })

        std_price_processor = lambda price, lead: self.__standart_price_processor(price, lead)

        metrics.extend(self.get_metrics_from_leads(res.json()['leads'], 1212574, "licenses", 'лицензий', 'лицензии', lambda price, lead: self.__standart_price_processor(price/2, lead)))
        metrics.extend(self.get_metrics_from_leads(res.json()['leads'], [1693720, 4669350], "widgets", 'Виджетов', 'виджеты', std_price_processor))
        metrics.extend(self.get_metrics_from_leads(res.json()['leads'], [1693621, 3346951], "projects", 'Проектов', 'проекты', std_price_processor))
        metrics.extend(self.get_metrics_from_leads(res.json()['leads'], 3941655, "courses", 'Курсов', 'курсы', std_price_processor))

        metrics.append(Metrica("Аудитов продано", len(audits_leads_res.json()['leads']), 'audits'))
        
        metrics.append(Metrica(
            "Денег за аудиты",
            500 * len(audits_leads_res.json()['leads']),
            group = 'audits',
            label='audits_money',
            meta_params = {self.META_PARAM_COUNT_IN_TOTAL_SUM: True}
        ))

        hours_list = [self.__find_custom_field_value_in_lead(lead, 682570) for lead in projects_worktime_leads.json()['leads']]
        hours_list = [int(a) for a in hours_list if a is not None]

        metrics.append(Metrica(
            "Часов на реализацию проектов затрачено",
            sum(hours_list),
            group = 'work_hours',
            label = 'work_hours_amount'
        ))

        if self.__employee.one_hour_salary_amount:
            metrics.append(Metrica(
                "Денег за рабочие часы по проектам",
                self.__employee.one_hour_salary_amount * self.__report.get_metrica_by_label('work_hours_amount').value,
                group = 'work_hours',
                label = 'work_hours_money',
                meta_params = {self.META_PARAM_COUNT_IN_TOTAL_SUM: True}
            ))

        if self.__employee.one_feedback_cost:

            feedback_count = [self.__find_custom_field_value_in_lead(lead, 683742) for lead in success_leads if lead['pipeline_id'] in [3964107, 3678177]]
            feedback_count = [int(a) if a else 1 for a in feedback_count]
            
            metrics.append(Metrica(
                "Отзывов собрано",
                sum(feedback_count),
                group = 'feedbacks',
                label = 'feedbacks_count'
            ))

            metrics.append(Metrica(
                "Денег за отзывы",
                self.__employee.one_feedback_cost * self.__report.get_metrica_by_label('feedbacks_count').value,
                group = 'feedbacks',
                label = 'feedbacks_money',
                meta_params = {self.META_PARAM_COUNT_IN_TOTAL_SUM: True}
            ))

        return metrics

    def __find_custom_field_value_in_lead(self, lead_obj, field_id):
        cf_values = lead_obj.get('custom_fields_values', None)
        if cf_values:
            for cf in cf_values:
                if cf['field_id'] == field_id:
                    return cf['values'][0]['value']
        return None

    def __get_metrics_for_salary(self, timestamp_from, timestamp_to):
        metrics = []
        if not self.__employee.daily_salary_amount:
            return metrics
        metrics.append(Metrica(
            "Оклад",
            math.ceil(self.__employee.daily_salary_amount*((timestamp_to-timestamp_from)/(3600 * 24))),
            group = 'salary',
            label = 'salary',
            meta_params = {self.META_PARAM_COUNT_IN_TOTAL_SUM: True}
        ))
        return metrics
    
    def __get_metrics_for_outcome_messages(self, timestamp_from, timestamp_to):
        metrics = []
        if not self.__employee.outcome_message_cost:
            return metrics

        base_url = "https://mazdata.ru/deltasales/get-events-by-filter"

        request_base_params = {
            'auth_key': 'oweiurghw85gh74o8m7h48',
            "filter": {
                "created_at": {
                    "from": timestamp_from,
                    "to": timestamp_to
                },
                "created_by": self.__employee.amocrm_id,
                "types": ['outgoing_chat_message']
            }
        }

        f = ApiIterator(base_url, params=request_base_params, entity_type='events', fetch_limit=50)
        num_of_messages = 0
        for msg in f.get_next():
            num_of_messages += 1

        metrics.append(Metrica(
            "Количество отправленных сообщений",
            num_of_messages,
            group = 'outcome_messages',
            label = 'outcome_messages_count'
        ))

        metrics.append(Metrica(
            "Денег за отправленные сообщения",
            num_of_messages * self.__employee.outcome_message_cost,
            group = 'outcome_messages',
            label='outcome_messages_money',
            meta_params = {self.META_PARAM_COUNT_IN_TOTAL_SUM: True}
        ))

        return metrics


    def get_detailed_report(self, timestamp_from, timestamp_to):
        report = Report()
        report.add_metrics(self.__get_metrics_for_calls(timestamp_from, timestamp_to))
        report.add_metrics(self.__get_metrics_for_amo_leads(timestamp_from, timestamp_to))
        report.add_metrics(self.__get_metrics_for_salary(timestamp_from, timestamp_to))
        report.add_metrics(self.__get_metrics_for_outcome_messages(timestamp_from, timestamp_to))
        money_amount = sum([metrica.value for metrica in report.get_metrics_by_meta_param(self.META_PARAM_COUNT_IN_TOTAL_SUM, True)])
        report.add_metrica(Metrica("Денег всего", money_amount))
        return report
    
    def __standart_price_processor(self, price, lead):
        lead_outcome = self.__find_custom_field_value_in_lead(lead, 683324)
        if lead_outcome:
            return price - int(lead_outcome)
        return price

    def get_metrics_from_leads(
        self,
        leads_list,
        pipeline_id_list,
        group,
        entity_name,
        entity_name_plural,
        lead_price_processor = lambda price, lead: price):

            if not isinstance(pipeline_id_list, list):
                pipeline_id_list = [pipeline_id_list]
                
            return [
                Metrica(entity_name + " продано", len([lead for lead in leads_list if lead['pipeline_id'] in pipeline_id_list]), group),
                Metrica(entity_name + " продано на сумму", sum([lead['price'] for lead in leads_list if lead['pipeline_id'] in pipeline_id_list]), group),
                
                Metrica(
                    "Денег за " + entity_name_plural,
                    math.floor(sum([lead_price_processor(lead['price'], lead)*((self.__employee.sale_fee_percent if self.__employee.sale_fee_percent else 0)/100) for lead in leads_list if lead['pipeline_id'] in pipeline_id_list])),
                    group = group,
                    label = group+"_money",
                    meta_params = {self.META_PARAM_COUNT_IN_TOTAL_SUM: True}
                ) 
            ]
