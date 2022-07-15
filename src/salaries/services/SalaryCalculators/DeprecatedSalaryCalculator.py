from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCounter import SalaryCounter

class DeprecatedSalaryCalculator(AbstractSalaryCalculator):
    def process(self, employee, timestamp_from, timestamp_to):
        salary_counter = SalaryCounter(employee)
        return salary_counter.get_detailed_report(timestamp_from, timestamp_to)