import pytest

from salaries.services.SalaryCalculators.metrics_builders import MetricaBuilder

class MockMetricaBuilder(MetricaBuilder):
    DEFAULT_NAME = 'Test name'
    DEFAULT_LABEL = 'Test label'
    DEAFULT_GROUP = 'Test group'

def test_mock_metrica_builder():

    def calc(builder, employee, timestamp_from, timestamp_to, *args, **kwargs):
        return timestamp_from - timestamp_to

    builder = MockMetricaBuilder(value_func=calc)

    assert builder.metrica_name == 'Test name'
    metrica = builder.create(None, 100, 60)
    assert metrica.name == 'Test name'
    assert metrica.value == 40