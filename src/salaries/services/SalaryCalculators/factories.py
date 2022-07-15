from salaries.models.EmployeePosition import EmployeePosition
from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCalculators.DeprecatedSalaryCalculator import DeprecatedSalaryCalculator
from salaries.services.SalaryCalculators.SalesManagerSalaryCalculator import SalesManagerSalaryCalculator

POSITION_CALCULATORS = {
    EmployeePosition.DEPRECATED: DeprecatedSalaryCalculator,
    EmployeePosition.SALES_MANAGER: SalesManagerSalaryCalculator
}


def get_calculator_by_position_type(position):
    CalculatorClass = POSITION_CALCULATORS.get(position)
    if issubclass(CalculatorClass, AbstractSalaryCalculator):
        return CalculatorClass()
    return None