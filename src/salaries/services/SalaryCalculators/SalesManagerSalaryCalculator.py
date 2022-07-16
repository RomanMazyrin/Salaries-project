from salaries.models.Employee import Employee
from salaries.models.EmployeePosition import EmployeePosition
from salaries.models.SalaryReport import Metrica, SalaryReport
from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCalculators.constants import (
    LEADS_STATUSES_FOR_SALES_CALCULATIONS,
    META_PARAM_COUNT_IN_TOTAL_SUM,
    METRICA_MONEY_CLASS_NAME
)
from salaries.services.SalaryCalculators.helpers import (
    base_aggregated_values_calculator_factory,
    calculate_sum_value_over_leads_per_months,
    fetch_all_leads_by_months_covered_by_timestamp_interval
)


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

    def get_metrics_for_sales(
            self,
            leads_by_months,
            timestamp_from,
            timestamp_to,
            position: EmployeePosition):

        leads_by_months = self.cut_months_leads_closed_after_timestamp(
            leads_by_months, timestamp_to
        )

        (sales_money_values_calculator,
         sales_count_values_calculator) = base_aggregated_values_calculator_factory(
            position, timestamp_from, timestamp_to
        ).values()

        return [
            Metrica(
                "Сумма продаж",
                calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_money_values_calculator.sum),
                group='sales',
                label='sales_income'
            ),

            self.get_metrica_sales_fee_sum(leads_by_months, timestamp_from, timestamp_to, position),

            Metrica(
                'Бонусы за выполнение плана по продажам',
                calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_money_values_calculator.bonus_for_plan),
                group='sales',
                label='sales_plan_bonuses',
                meta_params={META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=METRICA_MONEY_CLASS_NAME
            ),

            Metrica(
                "Количество продаж",
                calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_count_values_calculator.sum),
                group='sales',
                label='sales_count'
            ),

            Metrica(
                'Бонусы за выполнение плана по количеству продаж',
                calculate_sum_value_over_leads_per_months(
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
        
        return report

