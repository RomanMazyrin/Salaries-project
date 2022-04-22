import json
import math

from packages.Sipuni.Constants import ACCEPTED_CALL_STATE, ANY_CALL_STATE
from packages.Sipuni.Constants import INBOUND_CALL_TYPE, OUTBOUND_CALL_TYPE
from .Metrica import Metrica
from .Report import Report
from amocrm_components.ApiIterator import ApiIterator
from datetime import datetime
import pytz
import imaplib
import asyncio
from functools import wraps, partial


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


ONE_WEEK_IN_SECONDS = 604800


class SalaryCounter:

    META_PARAM_COUNT_IN_TOTAL_SUM = 'COUNT_IN_TOTAL_SUM'
    AUTH_KEY = 'oweiurghw85gh74o8m7h48'
    LEADS_FETCH_URL = 'https://mazdata.ru/deltasales/get-leads-by-filter'
    EVENTS_FETCH_URL = 'https://mazdata.ru/deltasales/get-events-by-filter'
    TOTAL_MONEY_CLASS_NAME = 'success'
    METRICA_MONEY_CLASS_NAME = 'warning'
    METRICA_ERROR_CLASS_NAME = 'danger'

    COLD_CALLS_PIPELINE_ID = 3636822

    def __init__(self, employee, onpbx_client, sipuni_client):
        self.__employee = employee
        self.__onpbx_client = onpbx_client
        self.__sipuni_client = sipuni_client

    def __get_metrics_for_calls(self, timestamp_from, timestamp_to):

        metrics = []

        if not self.__employee.onpbx_id:
            return metrics

        onpbx_calls_outbound = []
        onpbx_calls_inbound = []

        week_boundary_from = timestamp_from
        week_boundary_to = week_boundary_from + ONE_WEEK_IN_SECONDS

        if week_boundary_to > timestamp_to:
            week_boundary_to = timestamp_to

        while True:

            onpbx_calls_outbound.extend(self.__onpbx_client.call_history.get(
                accountcode='outbound',
                caller_id_number=str(self.__employee.onpbx_id),
                start_stamp_from=int(week_boundary_from),
                start_stamp_to=int(week_boundary_to),
                duration_from=self.__employee.min_call_length + 1
            ))

            onpbx_calls_inbound.extend(self.__onpbx_client.call_history.get(
                accountcode='inbound',
                destination_number=str(self.__employee.onpbx_id),
                start_stamp_from=int(week_boundary_from),
                start_stamp_to=int(week_boundary_to),
                user_talk_time_from=self.__employee.min_call_length + 1
            ))

            week_boundary_from += ONE_WEEK_IN_SECONDS
            week_boundary_to += ONE_WEEK_IN_SECONDS

            if week_boundary_to > timestamp_to:
                week_boundary_to = timestamp_to

            if week_boundary_from >= timestamp_to:
                break

        timezone = pytz.timezone("Europe/Moscow")
        date_from = datetime.fromtimestamp(timestamp_from, timezone)
        date_to = datetime.fromtimestamp(timestamp_to, timezone)

        date_format = "%d.%m.%Y"

        sipuni_outbound_calls = self.__sipuni_client.calls_stats.get(
            call_type=OUTBOUND_CALL_TYPE,
            from_number=self.__employee.sipuni_id,
            state=ANY_CALL_STATE,
            from_date=date_from.strftime(date_format),
            to_date=date_to.strftime(date_format)
        )

        sipuni_outbound_calls_count = len(list(filter(
            lambda call: int(call.call_duration) >= 20,
            sipuni_outbound_calls
        )))

        sipuni_inbound_calls = self.__sipuni_client.calls_stats.get(
            call_type=INBOUND_CALL_TYPE,
            from_number=self.__employee.sipuni_id,
            state=ACCEPTED_CALL_STATE,
            from_date=date_from.strftime(date_format),
            to_date=date_to.strftime(date_format)
        )

        sipuni_inbound_calls_count = len(list(filter(
            lambda call: int(call.talk_duration) >= 20,
            sipuni_inbound_calls
        )))

        calls_outbound_total_count = len(onpbx_calls_outbound) + sipuni_outbound_calls_count
        calls_inbound_total_count = len(onpbx_calls_inbound) + sipuni_inbound_calls_count
        calls_total_count = calls_outbound_total_count + calls_inbound_total_count

        metrics.append(Metrica("Кол-во исходящих звонков", calls_outbound_total_count, 'calls'))
        metrics.append(Metrica("Кол-во входящих звонков", calls_inbound_total_count, 'calls'))
        metrics.append(Metrica("Кол-во звонков всего", calls_total_count, 'calls'))

        one_call_cost = self.__employee.one_call_cost if self.__employee.one_call_cost else 0

        metrics.append(Metrica(
            "Денег за звонки",
            int(one_call_cost * calls_total_count),
            group='calls',
            label='calls_money',
            meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=self.METRICA_MONEY_CLASS_NAME
        ))

        return metrics

    def __get_metrics_for_sales(self, timestamp_from, timestamp_to):
        metrics = []

        if not self.__employee.amocrm_id:
            return metrics

        leads = self.__get_closed_leads_with_payments_amounts(timestamp_from, timestamp_to)

        if self.__employee.sale_fee_percent:

            metrics.extend(self.get_metrics_from_leads(
                leads, 1212574, "licenses", 'лицензий', 'лицензии'))
            metrics.extend(self.get_metrics_from_leads(
                leads, [1693720, 4669350], "widgets", 'Виджетов', 'виджеты'))
            metrics.extend(self.get_metrics_from_leads(
                leads, [1693621, 3346951], "projects", 'Проектов', 'проекты'))
            metrics.extend(self.get_metrics_from_leads(
                leads, 3941655, "courses", 'Курсов', 'курсы'))

        if self.__employee.one_hour_salary_amount:
            hours_list = [self.__find_custom_field_value_in_lead(lead, 682570) for (
                lead, payment) in leads if lead['pipeline_id'] in [3346951]]
            hours_list = [int(a) for a in hours_list if a is not None]

            total_hours_sum = sum(hours_list)

            metrics.append(Metrica(
                "Часов на реализацию проектов затрачено",
                total_hours_sum,
                group='work_hours',
                label='work_hours_amount'
            ))

            metrics.append(Metrica(
                "Денег за рабочие часы по проектам",
                self.__employee.one_hour_salary_amount * total_hours_sum,
                group='work_hours',
                label='work_hours_money',
                meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=self.METRICA_MONEY_CLASS_NAME
            ))

        if self.__employee.one_feedback_cost:

            feedback_count = [self.__find_custom_field_value_in_lead(lead, 683742) for (
                lead, payment) in leads if lead['pipeline_id'] in [3964107, 3678177]]
            feedback_count = [int(a) if a else 1 for a in feedback_count]

            metrics.append(Metrica(
                "Отзывов собрано",
                sum(feedback_count),
                group='feedbacks',
                label='feedbacks_count'
            ))

            metrics.append(Metrica(
                "Денег за отзывы",
                self.__employee.one_feedback_cost * sum(feedback_count),
                group='feedbacks',
                label='feedbacks_money',
                meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=self.METRICA_MONEY_CLASS_NAME
            ))

        if self.__employee.cold_call_success_lead_cost:
            cold_calls_success_leads = [
                lead for (lead, payment) in leads
                if lead['pipeline_id'] == self.COLD_CALLS_PIPELINE_ID
            ]
            cold_calls_success_leads_count = len(cold_calls_success_leads)
            metrics.append(Metrica(
                "Успешных сделок по прозвону",
                cold_calls_success_leads_count,
                group='cold_calls',
                label='cold_calls_count'
            ))
            metrics.append(Metrica(
                "Денег за успешные сделки по прозвону",
                cold_calls_success_leads_count * self.__employee.cold_call_success_lead_cost,
                group='cold_calls',
                label='cold_calls_money',
                meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=self.METRICA_MONEY_CLASS_NAME
            ))

        return metrics

    def __get_metrics_for_audits(self, timestamp_from, timestamp_to):

        metrics = []

        if not self.__employee.amocrm_id:
            return metrics

        if not self.__employee.audit_cost:
            return metrics

        leads = self.__fetch_all_entities(
            url=self.LEADS_FETCH_URL,
            params={
                'auth_key': self.AUTH_KEY,
                "filter": json.dumps({
                    "responsible_user_id": self.__employee.amocrm_id,
                    'custom_fields': {
                        '489154': {
                            "from": timestamp_from,
                            "to": timestamp_to
                        }
                    }
                })
            },
            entity_type='leads',
            fetch_limit=50
        )

        metrics.append(Metrica("Аудитов продано", len(leads), 'audits'))

        metrics.append(Metrica(
            "Денег за аудиты",
            self.__employee.audit_cost * len(leads),
            group='audits',
            label='audits_money',
            meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=self.METRICA_MONEY_CLASS_NAME
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

        total_days_of_work = (timestamp_to - timestamp_from) / (3600 * 24)

        metrics.append(Metrica(
            "Оклад",
            math.ceil(self.__employee.daily_salary_amount * total_days_of_work),
            group='salary',
            label='salary',
            meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=self.METRICA_MONEY_CLASS_NAME
        ))
        return metrics

    def __get_metrics_for_outcome_email_messages(self, timestamp_from, timestamp_to):

        metrics = []
        if not self.__employee.outcome_email_message_cost:
            return metrics

        try:
            num_of_messages = self.__get_email_outcome_messages_count_in_period(
                timestamp_from, timestamp_to)
            metrics.append(Metrica(
                "Количество отправленных Email сообщений",
                num_of_messages,
                group='outcome_email_messages',
                label='outcome_email_messages_count'
            ))

            metrics.append(Metrica(
                "Денег за отправленные Email сообщения",
                num_of_messages * self.__employee.outcome_email_message_cost,
                group='outcome_email_messages',
                label='outcome_email_messages_money',
                meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=self.METRICA_MONEY_CLASS_NAME
            ))
        except BaseException:
            metrics.append(Metrica(
                "Не удалось получить информацию об отправленных email сообщениях",
                '',
                group='outcome_email_messages',
                label='outcome_email_messages_error',
                class_name=self.METRICA_ERROR_CLASS_NAME
            ))

        return metrics

    def __get_email_outcome_messages_count_in_period(self, timestamp_from, timestamp_to):
        mail = imaplib.IMAP4_SSL(self.__employee.email_imap_address)
        mail.login(
            self.__employee.email_imap_login,
            self.__employee.email_imap_password
        )
        mailbox_list = mail.list()[1]

        for i, box in enumerate(mailbox_list):
            decoded = box.decode()
            if 'Sent' in decoded:
                path, box_id = decoded.split(' "|" ')
                box_id = box_id.strip('"')
                break

        mail.select(box_id)

        timezone = pytz.timezone("Europe/Moscow")

        date_from = datetime.fromtimestamp(timestamp_from, timezone)
        date_to = datetime.fromtimestamp(timestamp_to, timezone)

        date_format = "%d-%b-%Y"

        result, data = mail.search(None, '(since "{}" before "{}")'.format(
            date_from.strftime(date_format),
            date_to.strftime(date_format)
        ))

        ids = data[0].decode()
        id_list = ids.split()
        return len(id_list)

    def __get_metrics_for_outcome_messages(self, timestamp_from, timestamp_to):

        metrics = []
        if not self.__employee.outcome_message_cost:
            return metrics

        events = self.__fetch_all_entities(
            url=self.EVENTS_FETCH_URL,
            params={
                'auth_key': self.AUTH_KEY,
                "filter": {
                    "created_at": {
                        "from": timestamp_from,
                        "to": timestamp_to
                    },
                    "created_by": self.__employee.amocrm_id,
                    "types": ['outgoing_chat_message']
                }
            },
            entity_type='events',
            fetch_limit=50
        )

        num_of_messages = len(events)

        metrics.append(Metrica(
            "Количество отправленных сообщений",
            num_of_messages,
            group='outcome_messages',
            label='outcome_messages_count'
        ))

        metrics.append(Metrica(
            "Денег за отправленные сообщения",
            num_of_messages * self.__employee.outcome_message_cost,
            group='outcome_messages',
            label='outcome_messages_money',
            meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=self.METRICA_MONEY_CLASS_NAME
        ))

        return metrics

    def __get_amocrm_metrics(self, timestamp_from, timestamp_to):
        metrics = []
        metrics.extend(self.__get_metrics_for_sales(timestamp_from, timestamp_to))
        metrics.extend(self.__get_metrics_for_audits(timestamp_from, timestamp_to))
        metrics.extend(self.__get_metrics_for_outcome_messages(timestamp_from, timestamp_to))
        return metrics

    async def get_detailed_report(self, timestamp_from, timestamp_to):
        report = Report()
        async_requests = [
            async_wrap(self.__get_metrics_for_calls),
            async_wrap(self.__get_metrics_for_salary),
            async_wrap(self.__get_amocrm_metrics),
            async_wrap(self.__get_metrics_for_outcome_email_messages)
        ]

        results = await asyncio.gather(
            *([req(timestamp_from, timestamp_to) for req in async_requests])
        )

        for result in results:
            report.add_metrics(result)

        money_amount = sum([metrica.value for metrica in report.get_metrics_by_meta_param(
            self.META_PARAM_COUNT_IN_TOTAL_SUM, True)])

        report.add_metrica(Metrica(
            "Денег всего",
            money_amount,
            class_name=self.TOTAL_MONEY_CLASS_NAME
        ))

        return report

    def __standart_price_processor(self, lead):
        res = {"plan": lead['price'], "payment": lead['price']}
        return res

    def get_metrics_from_leads(
            self,
            leads_list,
            pipeline_id_list,
            group,
            entity_name,
            entity_name_plural):

        if not isinstance(pipeline_id_list, list):
            pipeline_id_list = [pipeline_id_list]

        return [
            Metrica(entity_name + " продано", len([lead for (lead, payment)
                    in leads_list if lead['pipeline_id'] in pipeline_id_list]), group),
            Metrica(entity_name + " продано на сумму", sum([lead['price'] for (
                lead, payment) in leads_list if lead['pipeline_id'] in pipeline_id_list]), group),

            Metrica(
                "Денег за " + entity_name_plural,
                math.floor(sum([payment_amount for (lead, payment_amount)
                           in leads_list if lead['pipeline_id'] in pipeline_id_list])),
                group=group,
                label=group + "_money",
                meta_params={self.META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=self.METRICA_MONEY_CLASS_NAME
            )
        ]

    def __fetch_all_entities(self, **kwargs):
        f = ApiIterator(**kwargs)
        entities = []
        for entity in f.get_next():
            entities.append(entity)
        return entities

    def __split_closed_leads_by_months(self, leads_list):
        result_map = {}
        for lead in leads_list:
            lead_closed_timestamp = lead['closed_at']
            closed_datetime = datetime.fromtimestamp(lead_closed_timestamp)
            lead_closed_month_key = (closed_datetime.month, closed_datetime.year)

            if not result_map.get(lead_closed_month_key):
                result_map[lead_closed_month_key] = []

            result_map[lead_closed_month_key].append(lead)

        return result_map

    def __get_closed_leads_with_payments_amounts(self, timestamp_from, timestamp_to):

        timezone = pytz.timezone("Europe/Moscow")

        left_timestamp_border = datetime.fromtimestamp(timestamp_from, timezone).replace(
            day=1, hour=0, minute=0, second=0).timestamp()
        right_timestamp_border = datetime.fromtimestamp(
            timestamp_to).replace(hour=23, minute=59, second=59).timestamp()

        leads = self.__fetch_all_entities(
            url=self.LEADS_FETCH_URL,
            params={
                'auth_key': self.AUTH_KEY,
                "filter": json.dumps({
                    "closed_at": {
                        "from": left_timestamp_border,
                        "to": right_timestamp_border
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
                        {"status_id": 142, "pipeline_id": 4669350},
                        {"status_id": 142, "pipeline_id": self.COLD_CALLS_PIPELINE_ID}
                    ]
                })
            },
            entity_type='leads',
            fetch_limit=50
        )

        leads.sort(key=lambda lead: lead['closed_at'])

        splited_leads = self.__split_closed_leads_by_months(leads)

        result_list = []

        for (month_key, month_leads) in splited_leads.items():
            month_sum = 0
            for lead in month_leads:

                lead_price = self.__standart_price_processor(lead)

                month_sum += lead_price['plan']
                if lead['closed_at'] >= timestamp_from:
                    lead_percent = self.__employee.sale_fee_percent
                    if self.__employee.sales_plan is not None:
                        if month_sum <= self.__employee.sales_plan:
                            lead_percent = self.__employee.sale_fee_percent
                        else:
                            lead_percent = self.__employee.sale_fee_percent_above_plan

                        if not lead_percent:
                            lead_percent = self.__employee.sale_fee_percent

                    if not lead_percent:
                        lead_percent = 0

                    result_list.append((lead, lead_price['payment'] * (lead_percent / 100)))

        return result_list
