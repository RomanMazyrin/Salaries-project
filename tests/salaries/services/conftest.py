import pytest
from pathlib import Path
import os
from salaries.models.SalaryReport import SalaryReport
from salaries.models.Employee import Employee


@pytest.fixture
def tinkoff_payment_sheet_file_path():
    filename = "tinkoff_sheet.xlsx"
    filepath = Path(__file__).resolve().parent / filename
    try:
        yield filepath
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@pytest.fixture
def employee():
    employee = Employee(id=1)
    return employee


@pytest.fixture
def salary_reports_list(employee):
    report = SalaryReport(employee=employee)
    return [report]