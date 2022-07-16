from abc import ABC, abstractmethod
from salaries.models.SalaryReport import SalaryReport


class AbstractSalaryCalculator(ABC):
    @abstractmethod
    def process(self, employee, timestamp_from, timestamp_to) -> SalaryReport:
        pass
