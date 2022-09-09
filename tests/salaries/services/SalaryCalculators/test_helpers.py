from salaries.services.SalaryCalculators.helpers import (
    get_dates_from_timestamp_interval,
    get_month_daily_salary,
)
import pytest
from datetime import datetime


@pytest.fixture
def timestamp_from_create():
    def creator(year, month, day):
        return datetime(year, month, day, 0, 0, 0).timestamp()

    return creator


@pytest.fixture
def timestamp_to_create():
    def creator(year, month, day):
        return datetime(year, month, day, 23, 59, 59).timestamp()

    return creator


def test_dates_from_timestamp_interval(timestamp_from_create, timestamp_to_create):
    result = get_dates_from_timestamp_interval(
        timestamp_from_create(2022, 7, 16), timestamp_to_create(2022, 7, 22)
    )

    assert len(result) == 7
    weekdays = [d.isoweekday() for d in result if d.isoweekday() <= 5]
    assert len(weekdays) == 5

def test_salary_intervals(timestamp_from_create):
    s = get_month_daily_salary(timestamp_from_create(2022, 8, 1), 40000)
    assert s == 1740