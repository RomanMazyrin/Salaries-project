import os

from salaries.services.sheet_generators import (
    generate_tinkoff_payment_sheet_by_salary_reports,
)


def test_tinkoff_sheet_generating(tinkoff_payment_sheet_file_path, salary_reports_list):
    generate_tinkoff_payment_sheet_by_salary_reports(
        tinkoff_payment_sheet_file_path, salary_reports_list
    )
    assert os.path.exists(tinkoff_payment_sheet_file_path)
