from salaries.models.EmployeePosition import EmployeePosition
from salaries.services.SalaryCalculators.helpers import (
    get_sales_head_amocrm_id_list_for_all_groups,
)


def calculate_total_sales_for_manager(employee, leads_list):
    return sum(
        [lead["price"] for lead in leads_list if lead["responsible_user_id"] == employee.amocrm_id]
    )


def calculate_total_sales_for_sales_head(employee, leads_list):
    amocrm_id_list = get_sales_head_amocrm_id_list_for_all_groups(employee)
    return sum(
        [lead["price"] for lead in leads_list if lead["responsible_user_id"] in amocrm_id_list]
    )


EMPLOYEE_POSITIONS_PROGRESS_CALCULATORS = {
    EmployeePosition.SALES_MANAGER: calculate_total_sales_for_manager,
    EmployeePosition.SALES_HEAD: calculate_total_sales_for_sales_head,
}


def calculate_sales_plan_progress(employee, leads_list):
    position = employee.position
    if position:
        plan = position.sales_plan_money if position.sales_plan_money is not None else 0
    else:
        plan = 0

    total_sales_calculator = EMPLOYEE_POSITIONS_PROGRESS_CALCULATORS[
        employee.position.position_type
    ]
    actual = total_sales_calculator(employee, leads_list)

    percent = 0 if plan == 0 else round((actual / plan) * 100, 2)
    return {
        "employee": employee,
        "actual": actual,
        "plan": plan,
        "percent": percent,
    }
