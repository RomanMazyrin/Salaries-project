from abc import ABC, abstractmethod
from salaries.services.SalaryCounter import SalaryCounter
from salaries.models.EmployeePosition import EmployeePosition


class AbstractSalaryCalculator(ABC):
    @abstractmethod
    def process(self, employee, timestamp_from, timestamp_to):
        pass


class DeprecatedSalaryCalculator(AbstractSalaryCalculator):
    def process(self, employee, timestamp_from, timestamp_to):
        salary_counter = SalaryCounter(employee)
        return salary_counter.get_detailed_report(timestamp_from, timestamp_to)


class SalesManagerSalaryCalculator(AbstractSalaryCalculator):
    def process(self, employee, timestamp_from, timestamp_to):
        pass


POSITION_CALCULATORS = {
    EmployeePosition.DEPRECATED: DeprecatedSalaryCalculator,
    EmployeePosition.SALES_MANAGER: SalesManagerSalaryCalculator
}


def get_calculator_by_position_type(position):
    CalculatorClass = POSITION_CALCULATORS.get(position)
    if issubclass(CalculatorClass, AbstractSalaryCalculator):
        return CalculatorClass()
    return None
