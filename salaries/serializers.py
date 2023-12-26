import json

from rest_framework import serializers

from salaries.models import Employee, SalaryReport


class JsonCustomField(serializers.JSONField):
    def to_representation(self, value):
        return json.loads(value)

    def to_internal_value(self, data):
        return json.dumps(data)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("name",)


class SalaryReportSerializer(serializers.ModelSerializer):
    metrics = JsonCustomField()
    slug_id = serializers.SlugField(read_only=True)
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = SalaryReport
        fields = "__all__"
