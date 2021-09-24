import json 
import requests
import math
from .Metrica import Metrica


class SalaryCounter:

    def __init__(self, employee, onpbx_client, report):
        self.__onpbx_client = onpbx_client
        self.__employee = employee
        self.__report = report

    def __fill_report_with_calls(self, timestamp_from, timestamp_to):
        if self.__employee.onpbx_id:
            res_outbound = self.__onpbx_client.call_history.get(
                accountcode='outbound',
                caller_id_number=str(self.__employee.onpbx_id),
                start_stamp_from=int(timestamp_from),
                start_stamp_to=int(timestamp_to),
                duration_from=21
            )

            res_inbound = self.__onpbx_client.call_history.get(
                accountcode='inbound',
                destination_number=str(self.__employee.onpbx_id),
                start_stamp_from=int(timestamp_from),
                start_stamp_to=int(timestamp_to),
                user_talk_time_from=21
            )

            self.__report.add_metrica(Metrica("Кол-во исходящих звонков", len(res_outbound), 'calls'))
            self.__report.add_metrica(Metrica("Кол-во входящих звонков", len(res_inbound), 'calls'))
            self.__report.add_metrica(Metrica("Кол-во звонков всего", len(res_inbound) + len(res_outbound), 'calls'))
            self.__report.add_metrica(Metrica("Денег за звонки", int((len(res_outbound) + len(res_inbound)) * (self.__employee.one_call_cost if self.__employee.one_call_cost else 0)), 'calls', label='calls_money'))

    def __fill_report_with_amo_leads(self, timestamp_from, timestamp_to):
        if self.__employee.amocrm_id:
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

            self.__report.add_metrics(self.get_metrics_from_leads(res.json()['leads'], 1212574, "licenses", 'лицензий', 'лицензии', lambda price, lead: self.__standart_price_processor(price/2, lead)))
            self.__report.add_metrics(self.get_metrics_from_leads(res.json()['leads'], [1693720, 4669350], "widgets", 'Виджетов', 'виджеты', std_price_processor))
            self.__report.add_metrics(self.get_metrics_from_leads(res.json()['leads'], [1693621, 3346951], "projects", 'Проектов', 'проекты', std_price_processor))
            self.__report.add_metrics(self.get_metrics_from_leads(res.json()['leads'], 3941655, "courses", 'Курсов', 'курсы', std_price_processor))

            self.__report.add_metrica(Metrica("Аудитов продано", len(audits_leads_res.json()['leads']), 'audits'))
            self.__report.add_metrica(Metrica("Денег за аудиты", 500 * len(audits_leads_res.json()['leads']), 'audits', label='audits_money'))

            hours_list = [self.__find_custom_field_value_in_lead(lead, 682570) for lead in projects_worktime_leads.json()['leads']]
            hours_list = [int(a) for a in hours_list if a is not None]

            self.__report.add_metrica(Metrica(
                "Часов на реализацию проектов затрачено",
                sum(hours_list),
                'work_hours',
                label='work_hours_amount'
            ))

            if self.__employee.one_hour_salary_amount:
                self.__report.add_metrica(Metrica(
                    "Денег за рабочие часы по проектам",
                    self.__employee.one_hour_salary_amount * self.__report.get_metrica_by_label('work_hours_amount').value,
                    'work_hours',
                    label='work_hours_money'
                ))

            if self.__employee.one_feedback_cost:

                feedback_count = [self.__find_custom_field_value_in_lead(lead, 683742) for lead in success_leads if lead['pipeline_id'] in [3964107, 3678177]]
                feedback_count = [int(a) if a else 1 for a in feedback_count]
                
                self.__report.add_metrica(Metrica(
                    "Отзывов собрано",
                    sum(feedback_count),
                    'feedbacks',
                    label='feedbacks_count'
                ))

                self.__report.add_metrica(Metrica(
                    "Денег за отзывы",
                    self.__employee.one_feedback_cost * self.__report.get_metrica_by_label('feedbacks_count').value,
                    'feedbacks',
                    label='feedbacks_money'
                ))


    def __find_custom_field_value_in_lead(self, lead_obj, field_id):
        cf_values = lead_obj.get('custom_fields_values', None)
        if cf_values:
            for cf in cf_values:
                if cf['field_id'] == field_id:
                    return cf['values'][0]['value']
        return None

    def __fill_report_with_salary(self, timestamp_from, timestamp_to):
        if self.__employee.daily_salary_amount:
            self.__report.add_metrica(Metrica("Оклад", math.ceil(self.__employee.daily_salary_amount*((timestamp_to-timestamp_from)/(3600 * 24))), 'salary', label='salary'))

    def get_detailed_report(self, timestamp_from, timestamp_to):

        self.__fill_report_with_calls(timestamp_from, timestamp_to)
        self.__fill_report_with_amo_leads(timestamp_from, timestamp_to)
        self.__fill_report_with_salary(timestamp_from, timestamp_to)

        labels_to_sum = [
            'calls_money',
            'widgets_money',
            'licenses_money',
            'projects_money',
            'courses_money',
            'audits_money',
            'salary',
            'work_hours_money',
            'feedbacks_money'
        ]

        money_amount = sum([self.__report.get_metrica_by_label(label).value for label in labels_to_sum if self.__report.get_metrica_by_label(label)])

        self.__report.add_metrica(Metrica("Денег всего", money_amount))

        return self.__report
    
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
                Metrica("Денег за " + entity_name_plural, math.floor(sum([lead_price_processor(lead['price'], lead)*((self.__employee.sale_fee_percent if self.__employee.sale_fee_percent else 0)/100) for lead in leads_list if lead['pipeline_id'] in pipeline_id_list])), group, label=group+"_money") 
            ]
