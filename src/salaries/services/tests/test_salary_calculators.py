from datetime import datetime
from salaries.models.Employee import Employee
from salaries.services.SalaryCalculators.AbstractSalaryCalculator import AbstractSalaryCalculator
from salaries.services.SalaryCalculators.DeprecatedSalaryCalculator import (
    DeprecatedSalaryCalculator
)
from salaries.services.SalaryCalculators.factories import POSITION_CALCULATORS, get_calculator_by_position_type
from salaries.services.SalaryCalculators.helpers import split_closed_leads_by_months

from salaries.models.EmployeePosition import EmployeePosition
import pytest


@pytest.fixture
def leads_factory():
    def create_lead(closed_at_datetime=None, price=0, status=None, pipeline=None, user_id=None):
        closed_at_timestamp = closed_at_datetime.timestamp()
        return {
            'price': price,
            'closed_at': closed_at_timestamp,
            'status_id': status,
            'pipeline_id': pipeline,
            'responsible_user_id': user_id
        }
    return create_lead

@pytest.fixture
def leads_list(leads_factory):
    return [
        leads_factory(datetime(2022, 4, 6, 15, 0, 0), 10000),
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
        leads_factory(datetime(2022, 6, 16, 15, 0, 0), 10000)
    ]

@pytest.fixture
def leads_by_months(leads_list):
    return split_closed_leads_by_months(leads_list)

@pytest.fixture
def leads_fetcher(leads_by_months):
    def f(*args, **kwargs):
        return {
            'leads': leads_by_months
        }
    return f

@pytest.fixture
def sm_employee():
    position = EmployeePosition(
        position_type=EmployeePosition.SALES_MANAGER,
        sales_plan_money=25000,
        sales_plan_count=3,
        sales_fee_percent=10,
        sales_fee_percent_above_plan=15,
        sales_plan_money_bonus=30000,
        sales_plan_count_bonus=15000
    )
    employee = Employee(position=position)
    return employee


@pytest.fixture
def sales_head_employee():
    position = EmployeePosition(
        position_type=EmployeePosition.SALES_HEAD,
        daily_salary_amount=3182,
        sales_plan_money=25000,
        sales_plan_count=3,
        sales_fee_percent=5,
        sales_plan_money_bonus=10000,
        sales_plan_count_bonus=10000
    )
    employee = Employee(position=position, name='Test head employee')
    return employee
    

@pytest.fixture
def calculator_generator(leads_fetcher):
    def generator(position):
        CalculatorClass = POSITION_CALCULATORS.get(position.position_type)
        if issubclass(CalculatorClass, AbstractSalaryCalculator):
            return CalculatorClass(leads_fetcher)
        return None
    return generator


def test_default_position_calculator():
    calculator = get_calculator_by_position_type(EmployeePosition.DEPRECATED)
    assert isinstance(calculator, DeprecatedSalaryCalculator)


@pytest.fixture
def samples_map_for_sales_manager_calculator(
    sm_employee,
    sales_head_employee,
):
    return [
        {
            'employee': sm_employee,
            'interval': {
                "from": datetime(2022, 5, 4, 0, 0, 0).timestamp(),
                'to': datetime(2022, 6, 14, 23, 59, 59).timestamp()
            },
            'expected_metrics_values': {
                'sales_income': 50000,
                'sales_fee_salary': 6000,
                'sales_plan_bonus': 60000,
                'sales_count': 5,
                'sales_plan_count_bonus': 30000
            },
        },
        {
            'employee': sm_employee,
            'interval': {
                "from": datetime(2022, 4, 6, 0, 0, 0).timestamp(),
                'to': datetime(2022, 4, 8, 23, 59, 59).timestamp()
            },
            'expected_metrics_values': {
                'sales_income': 20000,
                'sales_fee_salary': 2000,
                'sales_plan_bonus': 0,
                'sales_count': 2,
                'sales_plan_count_bonus': 0
            },
        },
        {
            'employee': sales_head_employee,
            'interval': {
                "from": datetime(2022, 6, 13, 0, 0, 0).timestamp(),
                'to':  datetime(2022, 6, 17, 23, 59, 59).timestamp()
            },
            'expected_metrics_values': {
                'salary': 15910
            },
        }
    ]


def test_calculator_metrics_results(
    samples_map_for_sales_manager_calculator,
    calculator_generator
):

    for sample in samples_map_for_sales_manager_calculator:
        employee = sample['employee']
        calculator = calculator_generator(employee.position)
        metrics = calculator.process(
            employee,
            sample['interval']['from'],
            sample['interval']['to']
        )
        for expected in sample['expected_metrics_values'].items():
            assert metrics.get_metrica_by('label', expected[0]).value == expected[1]