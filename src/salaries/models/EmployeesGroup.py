from django.db import models

from salaries.models.Employee import Employee


class EmployeeGroup(models.Model):

    group_name = models.CharField('Название группы', max_length=250)
    employee_list = models.ManyToManyField(
        Employee, related_name='groups_as_employee', verbose_name='Список участников', blank=True)
    group_heads = models.ManyToManyField(
        Employee, related_name='groups_as_head', verbose_name='Список руководителей', blank=True)

    def __str__(self):
        return self.group_name

    class Meta:
        verbose_name = 'Группа сотрудников'
        verbose_name_plural = 'Группы сотрудников'
