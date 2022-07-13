from salaries.services.SalaryCalculators import (
    get_calculator_by_position_type, DeprecatedSalaryCalculator
)
from salaries.models.EmployeePosition import EmployeePosition


def test_default_position_calculator():
    calculator = get_calculator_by_position_type(EmployeePosition.DEPRECATED)
    assert isinstance(calculator, DeprecatedSalaryCalculator)
