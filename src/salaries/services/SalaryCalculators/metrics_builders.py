from abc import ABC, abstractmethod

from salaries.models.SalaryReport import Metrica
from salaries.services.SalaryCalculators.helpers import (
    calculate_sum_value_over_leads_per_months
)


def get_items_in_timestamp_interval(items, key, timestamp_from, timestamp_to):
    return filter(
        lambda item: timestamp_from <= item[key] <= timestamp_to,
        items
    )

def cut_months_leads_closed_after_timestamp(leads_by_months, timestamp):
    res = {}
    for (month_key, month_leads) in leads_by_months.items():
        update_month_leads = []
        for lead in month_leads:
            if lead['closed_at'] <= timestamp:
                update_month_leads.append(lead)
        res[month_key] = update_month_leads
    return res


class MetricaBuilder(ABC):

    DEFAULT_NAME = ''
    DEFAULT_LABEL = ''
    DEFAULT_GROUP = ''
    
    def __init__(self, name=None, label=None, group=None, meta={}, class_name=''):
        self.metrica_name = name if name is not None else self.DEFAULT_NAME
        self.metrica_label = label if label is not None else self.DEFAULT_LABEL
        self.metrica_group = group if group is not None else self.DEFAULT_GROUP
        self.metrica_meta = meta
        self.metrica_class_name = class_name

    @abstractmethod
    def _calculate_value(self, employee, timestamp_from, timestamp_to, *args, **kwargs):
        pass

    def create(self, employee, timestamp_from, timestamp_to, *args, **kwargs):
        value = self._calculate_value(employee, timestamp_from, timestamp_to, *args, **kwargs)
        return Metrica(
            name=self.metrica_name,
            value=value,
            group=self.metrica_group,
            label=self.metrica_label,
            meta_params=self.metrica_meta,
            class_name=self.metrica_class_name
        )


class SimpleMetricaBuilder(MetricaBuilder):
    def __init__(self, value_func=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrica_value_func = value_func if value_func is not None else lambda: None

    def _calculate_value(self, employee, timestamp_from, timestamp_to, *args, **kwargs):
        return self.metrica_value_func(self, employee, timestamp_from, timestamp_to, *args, **kwargs)
        

class LeadsAggregatedValueMetricBuilder(MetricaBuilder):
    def __init__(self, item_value_getter, **kwargs):
        super().__init__(**kwargs)
        self._item_value_getter = item_value_getter

    
    
class LeadsSumAggregatedValueMetricaBuilder(LeadsAggregatedValueMetricBuilder):
    def _calculate_value(self, employee, timestamp_from, timestamp_to, *args, **kwargs):

        def _sum(items):
            items_in_interval = get_items_in_timestamp_interval(items, 'closed_at', timestamp_from, timestamp_to)
            return sum([self._item_value_getter(item) for item in items_in_interval])

        leads_by_months = kwargs['leads']
        sales_total_sum = calculate_sum_value_over_leads_per_months(leads_by_months, _sum)
        return sales_total_sum



class LeadsBonusArchievementValueMetricaBuilder(LeadsAggregatedValueMetricBuilder):

    def __init__(self, plan, bonus, **kwargs):
        super().__init__(**kwargs)
        self._plan_getter = plan
        self._bonus_getter = bonus
        
    def _calculate_value(self, employee, timestamp_from, timestamp_to, *args, **kwargs):
        leads_by_months = cut_months_leads_closed_after_timestamp(kwargs['leads'], timestamp_to)

        def process_bonus(items):
            
            items_in_interval = get_items_in_timestamp_interval(items, 'closed_at', timestamp_from, timestamp_to)

            sum_in_full_list = sum([self._item_value_getter(item) for item in items])
            value_for_period = sum([self._item_value_getter(item) for item in items_in_interval])
            value_in_full_list_above_plan = sum_in_full_list - self._plan_getter(employee)

            if 0 <= value_in_full_list_above_plan <= value_for_period:
                return self._bonus_getter(employee)
            return 0

        sales_total_sum = calculate_sum_value_over_leads_per_months(leads_by_months, process_bonus)
        return sales_total_sum
        


class LeadsSalesFeeValueMetricaBuilder(MetricaBuilder):

    def _calculate_value(self, employee, timestamp_from, timestamp_to, *args, **kwargs):

        leads_by_months = cut_months_leads_closed_after_timestamp(kwargs['leads'], timestamp_to)
        position = employee.position

        total_salary_money_for_sales = 0

        for (month_key, month_leads) in leads_by_months.items():
            leads_in_interval = filter(
                lambda lead: timestamp_from <= lead['closed_at'] <= timestamp_to,
                month_leads
            )
            sum_in_full_list = sum([lead['price'] for lead in month_leads])
            
            income_for_sales_in_period = sum([lead['price'] for lead in leads_in_interval])
            income_for_sales_in_period_above_the_plan = sum_in_full_list - position.sales_plan_money

            if income_for_sales_in_period_above_the_plan < 0:
                income_for_sales_in_period_above_the_plan = 0

            if income_for_sales_in_period_above_the_plan >= income_for_sales_in_period:
                income_for_sales_in_period_above_the_plan = income_for_sales_in_period

            below_plan_income = income_for_sales_in_period - \
                income_for_sales_in_period_above_the_plan

            total_salary_money_for_sales += below_plan_income * (position.sales_fee_percent / 100)
            total_salary_money_for_sales += income_for_sales_in_period_above_the_plan * \
                (position.sales_fee_percent_above_plan / 100)

        return total_salary_money_for_sales