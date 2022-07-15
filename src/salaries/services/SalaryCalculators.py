from abc import ABC, abstractmethod
from datetime import datetime
import json

import pytz
from amocrm_components.ApiIterator import ApiIterator
from salaries.models.Employee import Employee
from salaries.models.SalaryReport import Metrica, SalaryReport
from salaries.services.SalaryCounter import SalaryCounter
from salaries.models.EmployeePosition import EmployeePosition


class AbstractSalaryCalculator(ABC):
    @abstractmethod
    def process(self, employee, timestamp_from, timestamp_to) -> SalaryReport:
        pass


class DeprecatedSalaryCalculator(AbstractSalaryCalculator):
    def process(self, employee, timestamp_from, timestamp_to):
        salary_counter = SalaryCounter(employee)
        return salary_counter.get_detailed_report(timestamp_from, timestamp_to)


LEADS_STATUSES_FOR_SALES_CALCULATIONS = [
    {"status_id": 142, "pipeline_id": 1693621},
    {"status_id": 142, "pipeline_id": 3346951},
    {"status_id": 142, "pipeline_id": 1212574},
    {"status_id": 142, "pipeline_id": 1693720},
    {"status_id": 142, "pipeline_id": 4669350}
]

META_PARAM_COUNT_IN_TOTAL_SUM = 'COUNT_IN_TOTAL_SUM'
AUTH_KEY = 'oweiurghw85gh74o8m7h48'
LEADS_FETCH_URL = 'https://mazdata.ru/deltasales/get-leads-by-filter'
TOTAL_MONEY_CLASS_NAME = 'success'
METRICA_MONEY_CLASS_NAME = 'warning'
METRICA_ERROR_CLASS_NAME = 'danger'


def split_closed_leads_by_months(leads_list):
    result_map = {}
    for lead in leads_list:
        lead_closed_timestamp = lead['closed_at']
        closed_datetime = datetime.fromtimestamp(lead_closed_timestamp)
        lead_closed_month_key = (closed_datetime.month, closed_datetime.year)
        if not result_map.get(lead_closed_month_key):
            result_map[lead_closed_month_key] = []
        result_map[lead_closed_month_key].append(lead)
    return result_map


class LeadsFetcher:

    def fetch_all_amocrm_entities_by_filter(self, **kwargs):
        f = ApiIterator(**kwargs)
        entities = []
        for entity in f.get_next():
            entities.append(entity)
        return entities

    def fetch_all_leads_by_months_covered_by_timestamp_interval(
            self,
            timestamp_from,
            timestamp_to,
            user_id=None,
            statuses=None):

        timezone = pytz.timezone("Europe/Moscow")

        left_timestamp_border = datetime.fromtimestamp(timestamp_from, timezone).replace(
            day=1, hour=0, minute=0, second=0).timestamp()
        right_timestamp_border = datetime.fromtimestamp(
            timestamp_to).replace(hour=23, minute=59, second=59).timestamp()

        filter_params = {
            "closed_at": {
                "from": left_timestamp_border,
                "to": right_timestamp_border
            },
        }

        if user_id is not None:
            filter_params['responsible_user_id'] = user_id

        if statuses is not None:
            filter_params['statuses'] = statuses

        leads = self.fetch_all_amocrm_entities_by_filter(
            url=LEADS_FETCH_URL,
            params={
                'auth_key': AUTH_KEY,
                "filter": json.dumps(filter_params)
            },
            entity_type='leads',
            fetch_limit=50
        )

        leads.sort(key=lambda lead: lead['closed_at'])
        return split_closed_leads_by_months(leads)


class SalesManagerSalaryCalculator(AbstractSalaryCalculator):
    '''
    Список метрик:

    1. Сумма продаж в деньгах [x]
    2. Деньги за продажи [x]
    3. Бонус за выполнение плана по продажам в деньгах [x]
    4. Количество продаж [x]
    5. Бонус за выполнение плана по продажам в количестве
    6. Количество встреч
    7. Бонус за выполнение плана по количеству встреч
    8. Деньги за встречи
    '''

    def get_leads_in_interval(self, leads_by_months, timestamp_from, timestamp_to):
        leads_in_interval = []
        for (month_key, month_leads) in leads_by_months.items():
            leads_in_interval += filter(
                lambda lead: timestamp_from <= lead['closed_at'] <= timestamp_to,
                month_leads
            )
        return leads_in_interval

    def sum_values_from_leads_in_interval(
        self,
        leads_by_months,
        timestamp_from,
        timestamp_to,
        value_getter
    ):
        leads_in_interval = self.get_leads_in_interval(
            leads_by_months, timestamp_from, timestamp_to
        )
        return sum([value_getter(lead) for lead in leads_in_interval])

    def get_metrica_sales_total_sum(self, leads_by_months, timestamp_from, timestamp_to):
        total_sum = self.sum_values_from_leads_in_interval(
            leads_by_months,
            timestamp_from,
            timestamp_to,
            lambda lead: lead['price']
        )
        return Metrica(
            "Сумма продаж",
            total_sum,
            group='sales',
            label='sales_income'
        )

    def get_metrica_sales_count(self, leads_by_months, timestamp_from, timestamp_to):
        total_count = self.sum_values_from_leads_in_interval(
            leads_by_months,
            timestamp_from,
            timestamp_to,
            lambda lead: 1
        )
        return Metrica(
            "Количество продаж",
            total_count,
            group='sales',
            label='sales_count'
        )

    def get_month_leads_income_money_slices(
            self,
            month_leads,
            timestamp_from,
            timestamp_to,
            position):

        leads_in_interval = filter(
            lambda lead: timestamp_from <= lead['closed_at'] <= timestamp_to,
            month_leads
        )

        income_for_sales_in_month = sum([lead['price'] for lead in month_leads])
        plan = position.sales_plan_money

        return {
            'income_for_sales_in_period': sum([lead['price'] for lead in leads_in_interval]),
            'income_for_sales_in_period_above_the_plan': income_for_sales_in_month - plan
        }

    def get_metrica_sales_fee_sum(self, leads_by_months, timestamp_from, timestamp_to, position):
        total_salary_money_for_sales = 0

        for (month_key, month_leads) in leads_by_months.items():

            (income_for_sales_in_period,
             income_for_sales_in_period_above_the_plan) = self.get_month_leads_income_money_slices(
                month_leads, timestamp_from, timestamp_to, position
            ).values()

            if income_for_sales_in_period_above_the_plan < 0:
                income_for_sales_in_period_above_the_plan = 0

            if income_for_sales_in_period_above_the_plan >= income_for_sales_in_period:
                income_for_sales_in_period_above_the_plan = income_for_sales_in_period

            below_plan_income = income_for_sales_in_period - \
                income_for_sales_in_period_above_the_plan

            total_salary_money_for_sales += below_plan_income * (position.sales_fee_percent / 100)
            total_salary_money_for_sales += income_for_sales_in_period_above_the_plan * \
                (position.sales_fee_percent_above_plan / 100)

        return Metrica(
            'Процент от продаж',
            total_salary_money_for_sales,
            group='sales',
            label='sales_fee_salary',
            meta_params={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME
        )

    def get_metrica_sales_bonus_sum(self, leads_by_months, timestamp_from, timestamp_to, position):
        total_bonus_money_for_sales_plan = 0

        for (month_key, month_leads) in leads_by_months.items():

            (income_for_sales_in_period,
             income_for_sales_in_period_above_the_plan) = self.get_month_leads_income_money_slices(
                month_leads, timestamp_from, timestamp_to, position
            ).values()

            if 0 <= income_for_sales_in_period_above_the_plan <= income_for_sales_in_period:
                total_bonus_money_for_sales_plan += position.sales_plan_money_bonus

        return Metrica(
            'Бонусы за выполнение плана по продажам',
            total_bonus_money_for_sales_plan,
            group='sales',
            label='sales_plan_bonuses',
            meta_params={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME
        )

    def get_metrics_for_sales(self, leads_by_months, timestamp_from, timestamp_to, position):
        leads_by_months = self.cut_months_leads_closed_after_timestamp(
            leads_by_months, timestamp_to
        )

        return [
            self.get_metrica_sales_total_sum(leads_by_months, timestamp_from, timestamp_to),
            self.get_metrica_sales_fee_sum(leads_by_months, timestamp_from, timestamp_to, position),
            self.get_metrica_sales_bonus_sum(
                leads_by_months, timestamp_from, timestamp_to, position
            ),
            self.get_metrica_sales_count(leads_by_months, timestamp_from, timestamp_to)
        ]

    def cut_months_leads_closed_after_timestamp(self, leads_by_months, timestamp):
        res = {}
        for (month_key, month_leads) in leads_by_months.items():
            update_month_leads = []
            for lead in month_leads:
                if lead['closed_at'] <= timestamp:
                    update_month_leads.append(lead)
            res[month_key] = update_month_leads
        return res

    def process(self, employee: Employee, timestamp_from, timestamp_to):
        report = SalaryReport()
        leads_fetcher = LeadsFetcher()

        leads_by_months = leads_fetcher.fetch_all_leads_by_months_covered_by_timestamp_interval(
            timestamp_from,
            timestamp_to,
            employee.amocrm_id,
            LEADS_STATUSES_FOR_SALES_CALCULATIONS
        )

        report.add_metrics(self.get_metrics_for_sales(
            leads_by_months, timestamp_from, timestamp_to, employee.position))


POSITION_CALCULATORS = {
    EmployeePosition.DEPRECATED: DeprecatedSalaryCalculator,
    EmployeePosition.SALES_MANAGER: SalesManagerSalaryCalculator
}


def get_calculator_by_position_type(position):
    CalculatorClass = POSITION_CALCULATORS.get(position)
    if issubclass(CalculatorClass, AbstractSalaryCalculator):
        return CalculatorClass()
    return None
