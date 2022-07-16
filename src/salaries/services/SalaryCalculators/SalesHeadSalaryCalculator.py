import math
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
    fetch_all_leads_by_months_covered_by_timestamp_interval,
    get_dates_from_timestamp_interval
)


class SalesHeadSalaryCalculator(AbstractSalaryCalculator):

    def get_salary_metrica(self, position, timestamp_from, timestamp_to):

        interval_days = get_dates_from_timestamp_interval(timestamp_from, timestamp_to)
        work_days = len([d.isoweekday() for d in interval_days if d.isoweekday() <= 5])

        return Metrica(
            "Оклад",
            math.ceil(position.daily_salary_amount * work_days),
            group='salary',
            label='salary',
            meta_params={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME
        )

    def get_metrics_for_sales(self, leads_by_months, timestamp_from, timestamp_to, position):

        (sales_money_values_calculator,
         sales_count_values_calculator) = base_aggregated_values_calculator_factory(
            position, timestamp_from, timestamp_to
        ).values()

        sales_total_sum = calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_money_values_calculator.sum)

        sales_fee_salary = math.ceil(sales_total_sum * (position.sales_fee_percent / 100))

        return [
            Metrica(
                "Сумма продаж",
                sales_total_sum,
                group='sales',
                label='sales_income'
            ),

            Metrica(
                "Процент с продаж",
                sales_fee_salary,
                group='sales',
                label='sales_fee_salary',
                meta_params={META_PARAM_COUNT_IN_TOTAL_SUM: True},
                class_name=METRICA_MONEY_CLASS_NAME
            ),

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

    def process(self, employee, timestamp_from, timestamp_to):
        report = SalaryReport()

        amocrm_id_list = []

        groups_as_head = employee.groups_as_head.all()
        for group in groups_as_head:
            members = group.employee_list.all()
            amocrm_id_list += [member.amocrm_id for member in members]

        amocrm_id_list = list(set(amocrm_id_list))

        leads_by_months = fetch_all_leads_by_months_covered_by_timestamp_interval(
            timestamp_from,
            timestamp_to,
            amocrm_id_list,
            LEADS_STATUSES_FOR_SALES_CALCULATIONS
        )

        report.add_metrica(self.get_salary_metrica(employee.position, timestamp_from, timestamp_to))

        report.add_metrics(self.get_metrics_for_sales(
            leads_by_months, timestamp_from, timestamp_to, employee.position))

        return report
