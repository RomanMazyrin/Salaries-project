from datetime import datetime

from salaries.services.SalaryCalculators.metrics_builders import (
    SalaryPerDayMetricaBuilder,
)
from salaries.services.SalaryCalculators.SalesManagerSalaryCalculator import (
    get_audits_count,
    get_audits_money,
)


def test_calculator_metrics_results(samples_map_for_sales_manager_calculator, calculator_generator):
    for sample in samples_map_for_sales_manager_calculator:
        employee = sample["employee"]
        calculator = calculator_generator(employee.position)
        metrics = calculator.process(employee, sample["interval"]["from"], sample["interval"]["to"])
        for expected in sample["expected_metrics_values"].items():
            assert metrics.get_metrica_by("label", expected[0]).value == expected[1]


def test_audit_leads_values_calculators(sm_employee, leads_fetcher):
    leads_info = leads_fetcher()
    audits_count = get_audits_count(None, sm_employee, 1, 1, **leads_info)
    assert audits_count == 3
    audits_cost = get_audits_money(None, sm_employee, 1, 1, **leads_info)
    assert audits_cost == 600


def test_dynamic_salary_per_day(sm_employee):
    builder = SalaryPerDayMetricaBuilder()
    timestamp_from = datetime(2022, 2, 4, 0, 0, 0).timestamp()
    timestamp_to = datetime(2022, 5, 23, 23, 59, 59).timestamp()
    result_metrica = builder.create(sm_employee, timestamp_from, timestamp_to)
    assert result_metrica.value == 143129
