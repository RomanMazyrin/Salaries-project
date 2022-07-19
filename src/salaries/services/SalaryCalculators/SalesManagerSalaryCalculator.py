from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCalculators.constants import (
    META_PARAM_COUNT_IN_TOTAL_SUM,
    METRICA_MONEY_CLASS_NAME
)

from salaries.services.SalaryCalculators.metrics_builders import (
    LeadsBonusArchievementValueMetricaBuilder,
    LeadsSalesFeeValueMetricaBuilder,
    LeadsSumAggregatedValueMetricaBuilder
)

class SalesManagerSalaryCalculator(AbstractSalaryCalculator):

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
            label='sales_plan_bonus',
            group='sales',
            item_value_getter=lambda lead: lead['price'],
            plan=lambda employee: employee.position.sales_plan_money,
            bonus=lambda employee: employee.position.sales_plan_money_bonus,
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME
        ),
        LeadsBonusArchievementValueMetricaBuilder(
            name='Бонус за выполнение плана по количеству продаж',
            label='sales_plan_count_bonus',
            group='sales',
            item_value_getter=lambda lead: 1,
            plan=lambda employee: employee.position.sales_plan_count,
            bonus=lambda employee: employee.position.sales_plan_count_bonus,
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME
        ),
        LeadsSalesFeeValueMetricaBuilder(
            name='Процент с продаж',
            label='sales_fee_salary',
            group='sales',
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME
        )
    ]
    
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

