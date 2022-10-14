import json
from salaries.models.EmployeePosition import EmployeePosition
from salaries.services.SalaryCalculators import (
    AbstractSalaryCalculator,
    DeprecatedSalaryCalculator,
    SalesHeadSalaryCalculator,
    SalesManagerSalaryCalculator,
    TechSupportSalaryCalculator,
    fetch_all_leads_by_months_covered_by_timestamp_interval,
)
from salaries.services.SalaryCalculators.constants import (
    AMOCRM_LEAD_AUDIT_MANAGER_ID_FIELD_ID,
    AUTH_KEY,
    LEADS_FETCH_URL,
    LEADS_STATUSES_FOR_SALES_CALCULATIONS,
)
from salaries.services.SalaryCalculators.helpers import fetch_all_amocrm_entities_by_filter

POSITION_CALCULATORS = {
    EmployeePosition.DEPRECATED: DeprecatedSalaryCalculator,
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

    return {"leads": leads_by_months, "audit_leads": audit_leads}


def sales_head_leads_fetcher(employee, timestamp_from, timestamp_to):
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
