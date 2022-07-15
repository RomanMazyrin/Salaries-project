from salaries.models.Employee import Employee
from salaries.models.EmployeePosition import EmployeePosition
from salaries.models.SalaryReport import Metrica, SalaryReport
from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCalculators.constants import LEADS_STATUSES_FOR_SALES_CALCULATIONS, META_PARAM_COUNT_IN_TOTAL_SUM, METRICA_MONEY_CLASS_NAME
from salaries.services.SalaryCalculators.helpers import fetch_all_leads_by_months_covered_by_timestamp_interval

class AggregatedValuesCalculator:
    
    def __init__(
            self,
            value_getter,
            values_sum_plan,
            plan_bonus_value,
            timestamp_from,
            timestamp_to):

        self.value_getter = value_getter
        self.values_sum_plan = values_sum_plan
        self.plan_bonus_value = plan_bonus_value
        self.timestamp_from = timestamp_from
        self.timestamp_to = timestamp_to

    def get_items_in_timestamp_interval(self, items, key):
        return filter(
            lambda item: self.timestamp_from <= item[key] <= self.timestamp_to,
            items
        )

    def sum(self, items):
        items_in_interval = self.get_items_in_timestamp_interval(items, 'closed_at')
        return sum([self.value_getter(item) for item in items_in_interval])

    def bonus_for_plan(self, items):
        items_in_interval = self.get_items_in_timestamp_interval(items, 'closed_at')
        sum_in_full_list = sum([self.value_getter(item) for item in items])

        value_for_period = sum([self.value_getter(item) for item in items_in_interval])
        value_in_full_list_above_plan = sum_in_full_list - self.values_sum_plan

        if 0 <= value_in_full_list_above_plan <= value_for_period:
            return self.plan_bonus_value
        return 0


class SalesManagerSalaryCalculator(AbstractSalaryCalculator):
    '''
    Список метрик:

    1. Сумма продаж в деньгах [x]
    2. Деньги за продажи [x]
    3. Бонус за выполнение плана по продажам в деньгах [x]
    4. Количество продаж [x]
    5. Бонус за выполнение плана по продажам в количестве [x]
    6. Количество встреч
    7. Бонус за выполнение плана по количеству встреч
    8. Деньги за встречи
    '''

    def get_leads_params_slices_in_interval(
        self,
        leads_list,
        timestamp_from,
        timestamp_to,
        plan,
        lead_value_getter
    ):

        leads_in_interval = filter(
            lambda lead: timestamp_from <= lead['closed_at'] <= timestamp_to,
            leads_list
        )

        sum_in_full_list = sum([lead_value_getter(lead) for lead in leads_list])

        return {
            'value_for_period': sum([lead_value_getter(lead) for lead in leads_in_interval]),
            'value_for_period_above_plan': sum_in_full_list - plan
        }

    def get_metrica_sales_fee_sum(
            self,
            leads_by_months,
            timestamp_from,
            timestamp_to,
            position):

        total_salary_money_for_sales = 0

        for (month_key, month_leads) in leads_by_months.items():

            (income_for_sales_in_period,
             income_for_sales_in_period_above_the_plan) = self.get_leads_params_slices_in_interval(
                month_leads,
                timestamp_from,
                timestamp_to,
                position.sales_plan_money,
                lambda lead: lead['price']
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

    def calculate_sum_value_over_leads_per_months(self, leads_by_months, calculator):
        total = 0
        for (month_key, month_leads) in leads_by_months.items():
            total += calculator(month_leads)
        return total

    def get_metrics_for_sales(
            self,
            leads_by_months,
            timestamp_from,
            timestamp_to,
            position: EmployeePosition):

        leads_by_months = self.cut_months_leads_closed_after_timestamp(
            leads_by_months, timestamp_to
        )

        sales_money_values_calculator = AggregatedValuesCalculator(
            lambda lead: lead['price'],
            position.sales_plan_money,
            position.sales_plan_money_bonus,
            timestamp_from, timestamp_to
        )

        sales_count_values_calculator = AggregatedValuesCalculator(
            lambda lead: 1,
            position.sales_plan_count,
            position.sales_plan_count_bonus,
            timestamp_from, timestamp_to
        )

        return [
            Metrica(
                "Сумма продаж",
                self.calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_money_values_calculator.sum),
                group='sales',
                label='sales_income'
            ),

            self.get_metrica_sales_fee_sum(leads_by_months, timestamp_from, timestamp_to, position),

            Metrica(
                'Бонусы за выполнение плана по продажам',
                self.calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_money_values_calculator.bonus_for_plan),
                group='sales',
                label='sales_plan_bonuses',
                meta_params={META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=METRICA_MONEY_CLASS_NAME
            ),

            Metrica(
                "Количество продаж",
                self.calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_count_values_calculator.sum),
                group='sales',
                label='sales_count'
            ),

            Metrica(
                'Бонусы за выполнение плана по количеству продаж',
                self.calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_count_values_calculator.bonus_for_plan),
                group='sales',
                label='sales_plan_count_bonuses',
                meta_params={META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=METRICA_MONEY_CLASS_NAME
            )
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

        leads_by_months = fetch_all_leads_by_months_covered_by_timestamp_interval(
            timestamp_from,
            timestamp_to,
            employee.amocrm_id,
            LEADS_STATUSES_FOR_SALES_CALCULATIONS
        )

        report.add_metrics(self.get_metrics_for_sales(
            leads_by_months, timestamp_from, timestamp_to, employee.position))

