from datetime import datetime
import json
import pytz
from amocrm_components.ApiIterator import ApiIterator
from salaries.services.SalaryCalculators.constants import AUTH_KEY, LEADS_FETCH_URL


def split_closed_leads_by_months(leads_list):
    result_map = {}
    for lead in leads_list:
        lead_closed_timestamp = lead['closed_at']
        closed_datetime = datetime.fromtimestamp(lead_closed_timestamp)
        lead_closed_month_key = (closed_datetime.month, closed_datetime.year)
        if not result_map.get(lead_closed_month_key):
            result_map[lead_closed_month_key] = []
        result_map[lead_closed_month_key].append(lead)
    return result_map


    
def fetch_all_amocrm_entities_by_filter(self, **kwargs):
    f = ApiIterator(**kwargs)
    entities = []
    for entity in f.get_next():
        entities.append(entity)
    return entities


def fetch_all_leads_by_months_covered_by_timestamp_interval(
    self,
    timestamp_from,
    timestamp_to,
    user_id=None,
    statuses=None):

    timezone = pytz.timezone("Europe/Moscow")

    left_timestamp_border = datetime.fromtimestamp(timestamp_from, timezone).replace(
        day=1, hour=0, minute=0, second=0).timestamp()
    right_timestamp_border = datetime.fromtimestamp(
        timestamp_to).replace(hour=23, minute=59, second=59).timestamp()

    filter_params = {
        "closed_at": {
            "from": left_timestamp_border,
            "to": right_timestamp_border
        },
    }

    if user_id is not None:
        filter_params['responsible_user_id'] = user_id

    if statuses is not None:
        filter_params['statuses'] = statuses

    leads = self.fetch_all_amocrm_entities_by_filter(
        url=LEADS_FETCH_URL,
        params={
            'auth_key': AUTH_KEY,
            "filter": json.dumps(filter_params)
        },
        entity_type='leads',
        fetch_limit=50
    )

    leads.sort(key=lambda lead: lead['closed_at'])
    return split_closed_leads_by_months(leads)


class AggregatedValuesCalculator:
    
    def __init__(
            self,
            value_getter,
            values_sum_plan,
            plan_bonus_value,
            timestamp_from,
            timestamp_to):

        self.value_getter = value_getter
        self.values_sum_plan = values_sum_plan
        self.plan_bonus_value = plan_bonus_value
        self.timestamp_from = timestamp_from
        self.timestamp_to = timestamp_to

    def get_items_in_timestamp_interval(self, items, key):
        return filter(
            lambda item: self.timestamp_from <= item[key] <= self.timestamp_to,
            items
        )

    def sum(self, items):
        items_in_interval = self.get_items_in_timestamp_interval(items, 'closed_at')
        return sum([self.value_getter(item) for item in items_in_interval])

    def bonus_for_plan(self, items):
        items_in_interval = self.get_items_in_timestamp_interval(items, 'closed_at')
        sum_in_full_list = sum([self.value_getter(item) for item in items])

        value_for_period = sum([self.value_getter(item) for item in items_in_interval])
        value_in_full_list_above_plan = sum_in_full_list - self.values_sum_plan

        if 0 <= value_in_full_list_above_plan <= value_for_period:
            return self.plan_bonus_value
        return 0


def base_aggregated_values_calculator_factory(position, timestamp_from, timestamp_to):
    sales_money_values_calculator = AggregatedValuesCalculator(
        lambda lead: lead['price'],
        position.sales_plan_money,
        position.sales_plan_money_bonus,
        timestamp_from, timestamp_to
    )

    sales_count_values_calculator = AggregatedValuesCalculator(
        lambda lead: 1,
        position.sales_plan_count,
        position.sales_plan_count_bonus,
        timestamp_from, timestamp_to
    )

    return {
        'money_values_aggregator': sales_money_values_calculator,
        'count_values_aggregator': sales_count_values_calculator
    }

def calculate_sum_value_over_leads_per_months(leads_by_months, calculator):
    total = 0
    for (month_key, month_leads) in leads_by_months.items():
        total += calculator(month_leads)
    return total