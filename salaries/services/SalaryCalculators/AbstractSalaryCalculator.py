from abc import ABC

from salaries.models.SalaryReport import Metrica, SalaryReport
from salaries.services.SalaryCalculators.constants import (
    META_PARAM_COUNT_IN_TOTAL_SUM,
    TOTAL_MONEY_CLASS_NAME,
)


class AbstractSalaryCalculator(ABC):
    METRICS_BUILDERS = []

    def __init__(self, metrics_data_fetcher=None):
        if metrics_data_fetcher is None:

            def empty_data(*args, **kwargs):
                return {}

            self.metrics_data_fetcher = empty_data
        else:
            self.metrics_data_fetcher = metrics_data_fetcher

    def process(self, employee, timestamp_from, timestamp_to) -> SalaryReport:
        report = SalaryReport()
        report.add_metrics(self.__build_metrics(employee, timestamp_from, timestamp_to))

        money_amount = sum(
            [
                metrica.value
                for metrica in report.get_metrics_by_meta_param(META_PARAM_COUNT_IN_TOTAL_SUM, True)
            ]
        )

        report.add_metrica(
            Metrica(
                "Денег всего",
                money_amount,
                class_name=TOTAL_MONEY_CLASS_NAME,
                label="total_money",
            )
        )

        return report

    def get_metrics_data(self, employee, timestamp_from, timestamp_to):
        return self.metrics_data_fetcher(employee, timestamp_from, timestamp_to)

    def __build_metrics(self, *args, **kwargs):
        metrics_data = self.get_metrics_data(*args, **kwargs)
        metrics = [mb.create(*args, **kwargs, **metrics_data) for mb in self.METRICS_BUILDERS]
        return metrics
