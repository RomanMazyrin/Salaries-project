import xlsxwriter

def generate_tinkoff_payment_sheet_by_salary_reports(target_path, reports_queryset):
    workbook = xlsxwriter.Workbook(target_path)
    worksheet = workbook.add_worksheet()
    header = ('Номер', 'Фамилия', 'Имя', 'Отчество', 'Номер счета', 'Сумма', 'Назначение платежа', 'Код вида дохода.', 'БИК банка')
    results_map = {}
    employee_map = {}
    for report in reports_queryset:
        current_report_total_money = results_map.get(report.employee.id, 0)
        report_total = report.get_total_money_as_int()
        if report_total is None:
            report_total = 0
        results_map[report.employee.id] = current_report_total_money + int(report_total)
        employee_map[report.employee.id] = report.employee
    expenses = [
        header
    ]
    for i, result in enumerate(results_map.items()):
        employee = employee_map[result[0]]
        expenses.append(
            (i+1, employee.surname, employee.name, employee.middlename, employee.bank_account, result[1], employee.default_payment_details, 1)
        )
    for row, item in enumerate(expenses):
        for col, value in enumerate(item):
            worksheet.write(row, col, value)
    workbook.close()
