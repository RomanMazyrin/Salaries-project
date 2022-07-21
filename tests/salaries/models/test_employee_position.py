import pytest
from salaries.models.EmployeePosition import EmployeePosition


@pytest.fixture
def position():
    return EmployeePosition()


def test_default_employee_position(position: EmployeePosition):
    assert position.position_type == EmployeePosition.DEPRECATED
