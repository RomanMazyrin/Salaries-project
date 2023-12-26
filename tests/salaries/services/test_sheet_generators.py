import io

from salaries.services.sheet_generators import (
    generate_tinkoff_payment_sheet_by_salary_reports,
)


def test_tinkoff_sheet_generating(salary_reports_list):
    temp_in_memory_report_file = generate_tinkoff_payment_sheet_by_salary_reports(
        salary_reports_list
    )
    assert isinstance(temp_in_memory_report_file, io.BytesIO)
    assert temp_in_memory_report_file.tell() == 0
