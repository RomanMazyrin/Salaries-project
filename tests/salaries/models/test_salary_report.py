import pytest
from salaries.models.SalaryReport import SalaryReport, Metrica, MetricsCollection


@pytest.fixture
def report():
    return SalaryReport()


@pytest.fixture
def metrics_collection():
    collection = MetricsCollection()
    collection.add(Metrica("hello", "world", label="money"))
    collection.add(Metrica("test", "just", label="not money"))
    return collection


def test_adding_metrica(report: SalaryReport):

    report.add_metrica(Metrica("hello", "world", group="hello"))
    report.add_metrica(Metrica("hello", "world", group="hello"))
    report.add_metrica(Metrica("hello", "world", group="hello"))

    multiple_metrics = [
        Metrica("one", "value 1"),
        Metrica("two", "value 2", meta_params={"meta": "meta_value_1"}),
        Metrica("three", "value 3", meta_params={"meta": "meta_value_2"}),
    ]

    report.add_metrics(multiple_metrics)

    assert report.count_metrics() == 6

    with pytest.raises(TypeError):
        report.add_metrica("hello")


def test_getting_metrica(metrics_collection: MetricsCollection):
    assert metrics_collection.get_by("label", "money").value == "world"
    assert metrics_collection.get_by("label", "not money").value == "just"
