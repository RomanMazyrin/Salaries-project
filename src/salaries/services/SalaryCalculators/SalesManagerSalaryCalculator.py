from salaries.services.SalaryCalculators.AbstractSalaryCalculator import (
    AbstractSalaryCalculator,
)
from salaries.services.SalaryCalculators.constants import (
    AMOCRM_AUDIT_DATE_FIELD_ID,
    META_PARAM_COUNT_IN_TOTAL_SUM,
    METRICA_MONEY_CLASS_NAME,
)
from salaries.services.SalaryCalculators.helpers import get_lead_date_custom_field_value
from salaries.services.SalaryCalculators.metrics_builders import (
    LeadsBonusArchievementValueMetricaBuilder,
    LeadsSalesFeeValueMetricaBuilder,
    LeadsSumAggregatedValueMetricaBuilder,
    SalaryPerDayMetricaBuilder,
    SimpleMetricaBuilder,
)


def get_audits_count(builder, employee, timestamp_from, timestamp_to, *args, **kwargs):
    return len(kwargs["audit_leads"])


def get_audits_money(builder, employee, timestamp_from, timestamp_to, *args, **kwargs):
    audits_count = get_audits_count(
        builder, employee, timestamp_from, timestamp_to, *args, **kwargs
    )
    return audits_count * employee.position.one_audit_commit_cost


class SalesManagerSalaryCalculator(AbstractSalaryCalculator):

    METRICS_BUILDERS = [
        LeadsSumAggregatedValueMetricaBuilder(
            name="Сумма продаж",
            label="sales_income",
            group="sales",
            item_value_getter=lambda lead: lead["price"],
        ),
        LeadsSumAggregatedValueMetricaBuilder(
            name="Количество продаж",
            label="sales_count",
            group="sales",
            item_value_getter=lambda lead: 1,
        ),
        LeadsSumAggregatedValueMetricaBuilder(
            name="Количество проведенных встреч",
            label="demonstrations_count",
            group="demonstrations",
            item_value_getter=lambda lead: 1,
            leads_items_key="demonstration_leads",
            value_getter_to_time_intervals_split=lambda lead: get_lead_date_custom_field_value(
                lead, AMOCRM_AUDIT_DATE_FIELD_ID
            ).timestamp(),
        ),
        LeadsBonusArchievementValueMetricaBuilder(
            name="Бонус за выполнение плана по продажам в деньгах",
            label="sales_plan_bonus",
            group="sales",
            item_value_getter=lambda lead: lead["price"],
            plan=lambda employee: employee.position.sales_plan_money,
            bonus=lambda employee: employee.position.sales_plan_money_bonus,
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME,
        ),
        LeadsBonusArchievementValueMetricaBuilder(
            name="Бонус за выполнение плана по количеству продаж",
            label="sales_plan_count_bonus",
            group="sales",
            item_value_getter=lambda lead: 1,
            plan=lambda employee: employee.position.sales_plan_count,
            bonus=lambda employee: employee.position.sales_plan_count_bonus,
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME,
        ),
        LeadsBonusArchievementValueMetricaBuilder(
            name="Бонус за выполнение плана по встречам",
            label="demonstrations_plan_bonus",
            group="demonstrations",
            item_value_getter=lambda lead: 1,
            plan=lambda employee: employee.position.presentation_meetings_plan_count,
            bonus=lambda employee: employee.position.presentation_meetings_plan_count_bonus,
            leads_items_key="demonstration_leads",
            value_getter_to_time_intervals_split=lambda lead: get_lead_date_custom_field_value(
                lead, AMOCRM_AUDIT_DATE_FIELD_ID
            ).timestamp(),
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME,
        ),
        LeadsSalesFeeValueMetricaBuilder(
            name="Процент с продаж",
            label="sales_fee_salary",
            group="sales",
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME,
        ),
        SalaryPerDayMetricaBuilder(),
        SimpleMetricaBuilder(
            name="Количество назначенных аудитов",
            group="audits",
            label="audits_count",
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: False},
            value_func=get_audits_count,
        ),
        SimpleMetricaBuilder(
            name="Денег за назначенные аудиты",
            group="audits",
            label="audits_money",
            meta={META_PARAM_COUNT_IN_TOTAL_SUM: True},
            class_name=METRICA_MONEY_CLASS_NAME,
            value_func=get_audits_money,
        ),
    ]
