from datetime import datetime
from salaries.models.SalaryReport import MetricsCollection
from salaries.services.SalaryCalculators import (
    get_calculator_by_position_type, DeprecatedSalaryCalculator, split_closed_leads_by_months
)
from salaries.models.EmployeePosition import EmployeePosition
import pytest


@pytest.fixture
def leads_factory():
    def create_lead(closed_at_datetime=None, price=0, status=None, pipeline=None):
        if closed_at_datetime is None:
            closed_at_datetime = datetime.now()
        closed_at_timestamp = closed_at_datetime.timestamp()
        return {
            'price': price,
            'closed_at': closed_at_timestamp,
            'status_id': status,
            'pipeline_id': pipeline
        }
    return create_lead


@pytest.fixture
def leads_by_months(leads_factory):
    return split_closed_leads_by_months(
        [leads_factory(datetime(2022, 4, 6, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 4, 8, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 4, 10, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 4, 25, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 5, 1, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 5, 3, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 5, 5, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 5, 18, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 6, 2, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 6, 5, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 6, 14, 15, 0, 0), 10000),
         leads_factory(datetime(2022, 6, 16, 15, 0, 0), 10000)]
    )


@pytest.fixture
def sm_position():
    position = EmployeePosition(
        position_type=EmployeePosition.SALES_MANAGER,
        sales_plan_money=25000,
        sales_fee_percent=10,
        sales_fee_percent_above_plan=15,
        sales_plan_money_bonus=30000
    )
    return position


@pytest.fixture
def sales_manager_calculator(sm_position):
    return get_calculator_by_position_type(sm_position.position_type)


@pytest.fixture
def sales_metrics_collection_for_time_interval_generator(
        sales_manager_calculator,
        leads_by_months,
        sm_position):

    def generator(timestamp_from, timestamp_to):
        return MetricsCollection().extend(sales_manager_calculator.get_metrics_for_sales(
            leads_by_months,
            timestamp_from,
            timestamp_to,
            sm_position
        ))
    return generator


def test_default_position_calculator():
    calculator = get_calculator_by_position_type(EmployeePosition.DEPRECATED)
    assert isinstance(calculator, DeprecatedSalaryCalculator)


@pytest.fixture
def samples_map_for_sales_manager_calculator():
    return [
        {
            'interval': {
                "from": datetime(2022, 5, 4, 0, 0, 0).timestamp(),
                'to': datetime(2022, 6, 14, 23, 59, 59).timestamp()
            },
            'expected_metrics_values': {
                'sales_income': 50000,
                'sales_fee_salary': 6000,
                'sales_plan_bonuses': 60000
            },
        },
        {
            'interval': {
                "from": datetime(2022, 4, 6, 0, 0, 0).timestamp(),
                'to': datetime(2022, 4, 8, 23, 59, 59).timestamp()
            },
            'expected_metrics_values': {
                'sales_income': 20000,
                'sales_fee_salary': 2000,
                'sales_plan_bonuses': 0
            },
        }
    ]


def test_sales_manager_calculator_sales_metrics(
    samples_map_for_sales_manager_calculator,
    sales_metrics_collection_for_time_interval_generator
):

    for sample in samples_map_for_sales_manager_calculator:
        metrics = sales_metrics_collection_for_time_interval_generator(
            sample['interval']['from'],
            sample['interval']['to']
        )
        for expected in sample['expected_metrics_values'].items():
            assert metrics.get_by('label', expected[0]).value == expected[1]
