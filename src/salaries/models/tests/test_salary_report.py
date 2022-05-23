import pytest
from salaries.models.SalaryReport import SalaryReport, Metrica


@pytest.fixture
def report():
    return SalaryReport()


def test_adding_metrica(report: SalaryReport):

    report.add_metrica(Metrica('hello', 'world', group="hello"))
    report.add_metrica(Metrica('hello', 'world', group="hello"))
    report.add_metrica(Metrica('hello', 'world', group="hello"))

    multiple_metrics = [
        Metrica("one", "value 1"),
        Metrica("two", "value 2", meta_params={'meta': "meta_value_1"}),
        Metrica("three", "value 3", meta_params={'meta': "meta_value_2"})
    ]

    report.add_metrics(multiple_metrics)

    assert report.count_metrics() == 6

    with pytest.raises(TypeError):
        report.add_metrica("hello")
