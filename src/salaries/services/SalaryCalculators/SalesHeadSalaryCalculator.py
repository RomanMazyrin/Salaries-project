import math
from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCalculators.constants import (
    META_PARAM_COUNT_IN_TOTAL_SUM,
    METRICA_MONEY_CLASS_NAME
)
from salaries.services.SalaryCalculators.helpers import (
    get_dates_from_timestamp_interval
)
from salaries.services.SalaryCalculators.metrics_builders import (
    LeadsBonusArchievementValueMetricaBuilder,
    LeadsSumAggregatedValueMetricaBuilder,
    SimpleMetricaBuilder
)


def salary_per_days_calc(builder, employee, timestamp_from, timestamp_to, **kwargs):
    interval_days = get_dates_from_timestamp_interval(timestamp_from, timestamp_to)
    work_days = len([d.isoweekday() for d in interval_days if d.isoweekday() <= 5])
    return math.ceil(employee.position.daily_salary_amount * work_days)

def sales_fee_calc(builder, employee, timestamp_from, timestamp_to, *args, **kwargs):
    sum_builder = LeadsSumAggregatedValueMetricaBuilder(
        name='Сумма продаж',
        label='sales_income',
        group='sales',
        item_value_getter=lambda lead: lead['price']
    )

    sales_total_sum = sum_builder.create(employee, timestamp_from, timestamp_to, *args, **kwargs).value

    sales_fee_salary = math.ceil(sales_total_sum * (employee.position.sales_fee_percent / 100))
    return sales_fee_salary


class SalesHeadSalaryCalculator(AbstractSalaryCalculator):

    METRICS_BUILDERS = [
        LeadsSumAggregatedValueMetricaBuilder(
            name='Сумма продаж',
            label='sales_income',
            group='sales',
            item_value_getter=lambda lead: lead['price']
        ),
        LeadsSumAggregatedValueMetricaBuilder(
            name='Количество продаж',
            label='sales_count',
            group='sales',
            item_value_getter=lambda lead: 1
        ),
        LeadsBonusArchievementValueMetricaBuilder(
            name='Бонус за выполнение плана по продажам в деньгах',
            label='sales_money_bouns',
            group='sales',
            item_value_getter=lambda lead: lead['price'],
            plan=lambda employee: employee.position.sales_plan_money,
            bonus=lambda employee: employee.position.sales_plan_money_bonus,
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME
        ),
        LeadsBonusArchievementValueMetricaBuilder(
            name='Бонус за выполнение плана по количеству продаж',
            label='sales_count_bouns',
            group='sales',
            item_value_getter=lambda lead: 1,
            plan=lambda employee: employee.position.sales_plan_count,
            bonus=lambda employee: employee.position.sales_plan_count_bonus,
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME
        ),
        SimpleMetricaBuilder(
            name='Оклад',
            group='salary',
            label='salary',
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME,
            value_func=salary_per_days_calc
        ),
        SimpleMetricaBuilder(
            name="Процент с продаж",
            group='sales',
            label='sales_fee_salary',
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME,
            value_func=sales_fee_calc
        )
    ]