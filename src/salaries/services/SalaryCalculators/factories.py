import json

from salaries.models.EmployeePosition import EmployeePosition
from salaries.services.SalaryCalculators import (
    AbstractSalaryCalculator,
    SalesHeadSalaryCalculator,
    SalesManagerSalaryCalculator,
    TechSupportSalaryCalculator,
    fetch_all_leads_by_months_covered_by_timestamp_interval,
)
from salaries.services.SalaryCalculators.constants import (
    AMOCRM_AUDIT_DATE_FIELD_ID,
    AMOCRM_AUDIT_RECORD_LINK_FIELD_ID,
    AMOCRM_IS_AUDIT_CORRECT_FIELD_ID,
    AMOCRM_LEAD_AUDIT_MANAGER_ID_FIELD_ID,
    AUTH_KEY,
    LEADS_FETCH_URL,
    LEADS_STATUSES_FOR_SALES_CALCULATIONS,
)
from salaries.services.SalaryCalculators.helpers import (
    fetch_all_amocrm_entities_by_filter,
    get_borders_by_timestamp_interval,
    get_lead_custom_field_value,
    get_sales_head_amocrm_id_list_for_all_groups,
    split_leads_by_months_by_custom_date_field,
)

POSITION_CALCULATORS = {
    EmployeePosition.SALES_MANAGER: SalesManagerSalaryCalculator,
    EmployeePosition.SALES_HEAD: SalesHeadSalaryCalculator,
    EmployeePosition.FIXED_SALARY: TechSupportSalaryCalculator,
}


def employee_leads_fetcher(employee, timestamp_from, timestamp_to):
    leads_by_months = fetch_all_leads_by_months_covered_by_timestamp_interval(
        timestamp_from,
        timestamp_to,
        employee.amocrm_id,
        LEADS_STATUSES_FOR_SALES_CALCULATIONS,
    )
    audit_leads = fetch_all_amocrm_entities_by_filter(
        url=LEADS_FETCH_URL,
        params={
            "auth_key": AUTH_KEY,
            "filter": json.dumps(
                {
                    "custom_fields": {AMOCRM_LEAD_AUDIT_MANAGER_ID_FIELD_ID: employee.amocrm_id},
                    "created_at": {"from": timestamp_from, "to": timestamp_to},
                }
            ),
        },
        entity_type="leads",
        fetch_limit=50,
    )
    border_left, border_right = get_borders_by_timestamp_interval(timestamp_from, timestamp_to)
    demonstration_leads = fetch_all_amocrm_entities_by_filter(
        url=LEADS_FETCH_URL,
        params={
            "auth_key": AUTH_KEY,
            "filter": json.dumps(
                {
                    "custom_fields": {
                        AMOCRM_AUDIT_DATE_FIELD_ID: {"from": border_left, "to": border_right},
                        AMOCRM_IS_AUDIT_CORRECT_FIELD_ID: True,
                    },
                    "responsible_user_id": employee.amocrm_id,
                }
            ),
        },
        entity_type="leads",
        fetch_limit=50,
    )
    demonstration_leads_with_record = filter(
        lambda lead: get_lead_custom_field_value(lead, AMOCRM_AUDIT_RECORD_LINK_FIELD_ID),
        demonstration_leads,
    )
    demonstration_leads_by_month = split_leads_by_months_by_custom_date_field(
        demonstration_leads_with_record, AMOCRM_AUDIT_DATE_FIELD_ID
    )

    return {
        "leads": leads_by_months,
        "audit_leads": audit_leads,
        "demonstration_leads": demonstration_leads_by_month,
    }


def sales_head_leads_fetcher(employee, timestamp_from, timestamp_to):
    amocrm_id_list = get_sales_head_amocrm_id_list_for_all_groups(employee)

    leads_by_months = fetch_all_leads_by_months_covered_by_timestamp_interval(
        timestamp_from,
        timestamp_to,
        amocrm_id_list,
        LEADS_STATUSES_FOR_SALES_CALCULATIONS,
    )

    return {"leads": leads_by_months}


POSITION_LEADS_FETCHERS = {
    EmployeePosition.DEPRECATED: employee_leads_fetcher,
    EmployeePosition.SALES_MANAGER: employee_leads_fetcher,
    EmployeePosition.SALES_HEAD: sales_head_leads_fetcher,
}


def get_calculator_by_position_type(position_type):
    CalculatorClass = POSITION_CALCULATORS.get(position_type)
    if issubclass(CalculatorClass, AbstractSalaryCalculator):
        return CalculatorClass(POSITION_LEADS_FETCHERS.get(position_type))
    return None
