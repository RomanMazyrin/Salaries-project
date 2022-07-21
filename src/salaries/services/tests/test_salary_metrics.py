from salaries.services.SalaryCalculators.metrics_builders import MetricaBuilder


class MockMetricaBuilder(MetricaBuilder):
    DEFAULT_NAME = "Test name"
    DEFAULT_LABEL = "Test label"
    DEFAULT_GROUP = "Test group"

    def _calculate_value(self, employee, timestamp_from, timestamp_to, *args, **kwargs):
        return 40


def test_mock_metrica_builder():

    builder = MockMetricaBuilder()

    assert builder.metrica_name == "Test name"
    metrica = builder.create(None, 1, 1)
    assert metrica.name == "Test name"
    assert metrica.label == "Test label"
    assert metrica.group == "Test group"
    assert metrica.value == 40
