import math
from salaries.models.SalaryReport import Metrica, SalaryReport
from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCalculators.constants import LEADS_STATUSES_FOR_SALES_CALCULATIONS, META_PARAM_COUNT_IN_TOTAL_SUM, METRICA_MONEY_CLASS_NAME
from salaries.services.SalaryCalculators.helpers import base_aggregated_values_calculator_factory, calculate_sum_value_over_leads_per_months, fetch_all_leads_by_months_covered_by_timestamp_interval


class SalesHeadSalaryCalculator(AbstractSalaryCalculator):

    def get_salary_metrica(self, position, timestamp_from, timestamp_to):

        total_days_of_work = (timestamp_to - timestamp_from) / (3600 * 24)

        return Metrica(
            "Оклад",
            math.ceil(position.daily_salary_amount * total_days_of_work),
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

        return [
            Metrica(
                "Сумма продаж",
                calculate_sum_value_over_leads_per_months(
                    leads_by_months, sales_money_values_calculator.sum),
                group='sales',
                label='sales_income'
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

        leads_by_months = fetch_all_leads_by_months_covered_by_timestamp_interval(
            timestamp_from,
            timestamp_to,
            employee.amocrm_id,
            LEADS_STATUSES_FOR_SALES_CALCULATIONS
        )

        report.add_metrica(self.get_salary_metrica(employee.position, timestamp_from, timestamp_to))

        report.add_metrics(self.get_metrics_for_sales(
            leads_by_months, timestamp_from, timestamp_to, employee.position))
        
        return report