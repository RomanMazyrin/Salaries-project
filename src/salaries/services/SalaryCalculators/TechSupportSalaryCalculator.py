from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCalculators.metrics_builders import SalaryPerDayMetricaBuilder


class TechSupportSalaryCalculator(AbstractSalaryCalculator):
    METRICS_BUILDERS = [
        SalaryPerDayMetricaBuilder()
    ]