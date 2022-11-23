from datetime import datetime, timedelta
import json
import math
import pytz
from amocrm_components.ApiIterator import ApiIterator
from salaries.services.SalaryCalculators.constants import AUTH_KEY, LEADS_FETCH_URL


def get_lead_custom_field_value(lead, field_id, default=None):
    lead_custom_fields = lead["custom_fields_values"]
    for field in lead_custom_fields:
        if field["field_id"] == field_id:
            return field["values"][0]["value"]
    return default


def get_carbon_datetime_str_as_datetime(carbon_datetime_str):
    tz = pytz.timezone("UTC")
    dt = datetime.strptime(carbon_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt = tz.localize(dt)
    return dt


def get_lead_date_custom_field_value(lead, field_id, default=None):
    datetime_str = get_lead_custom_field_value(lead, field_id, default)
    return get_carbon_datetime_str_as_datetime(datetime_str)


def split_leads_by_months(leads_list, timestamp_getter):
    result_map = {}
    for lead in leads_list:
        timestamp_param = timestamp_getter(lead)
        closed_datetime = datetime.fromtimestamp(timestamp_param)
        timestamp_month_key = (closed_datetime.month, closed_datetime.year)
        if not result_map.get(timestamp_month_key):
            result_map[timestamp_month_key] = []
        result_map[timestamp_month_key].append(lead)
    return result_map


def split_closed_leads_by_months(leads_list):
    return split_leads_by_months(leads_list, lambda lead: lead["closed_at"])


def split_leads_by_months_by_custom_date_field(leads_list, field_id):
    return split_leads_by_months(
        leads_list, lambda lead: get_lead_date_custom_field_value(lead, field_id).timestamp()
    )


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def fetch_all_amocrm_entities_by_filter(**kwargs):
    f = ApiIterator(**kwargs)
    entities = []
    for entity in f.get_next():
        entities.append(entity)
    return entities


def get_borders_by_timestamp_interval(timestamp_from, timestamp_to):
    timezone = pytz.timezone("Europe/Moscow")

    left_timestamp_border = (
        datetime.fromtimestamp(timestamp_from, timezone)
        .replace(day=1, hour=0, minute=0, second=0)
        .timestamp()
    )
    right_timestamp_border = (
        datetime.fromtimestamp(timestamp_to).replace(hour=23, minute=59, second=59).timestamp()
    )
    return (left_timestamp_border, right_timestamp_border)


def fetch_all_leads_by_months_covered_by_timestamp_interval(
    timestamp_from, timestamp_to, user_id=None, statuses=None
):
    left_timestamp_border, right_timestamp_border = get_borders_by_timestamp_interval(
        timestamp_from, timestamp_to
    )

    filter_params = {
        "closed_at": {"from": left_timestamp_border, "to": right_timestamp_border},
    }

    if user_id is not None:
        filter_params["responsible_user_id"] = user_id

    if statuses is not None:
        filter_params["statuses"] = statuses

    leads = fetch_all_amocrm_entities_by_filter(
        url=LEADS_FETCH_URL,
        params={"auth_key": AUTH_KEY, "filter": json.dumps(filter_params)},
        entity_type="leads",
        fetch_limit=50,
    )

    leads.sort(key=lambda lead: lead["closed_at"])
    return split_closed_leads_by_months(leads)


def calculate_sum_value_over_leads_per_months(leads_by_months, calculator):
    total = 0
    for (month_key, month_leads) in leads_by_months.items():
        total += calculator(month_leads)
    return total


def get_dates_from_timestamp_interval(timestamp_from, timestamp_to):
    right_border = timestamp_from
    res = []
    while True:
        res += [datetime.fromtimestamp(right_border).replace(hour=0, minute=0, second=0)]
        right_border += 3600 * 24
        if right_border > timestamp_to:
            res += [datetime.fromtimestamp(timestamp_to).replace(hour=0, minute=0, second=0)]
            break

    return list(set(res))


def get_workdays_in_interval(timestamp_from, timestamp_to):
    interval_days = get_dates_from_timestamp_interval(timestamp_from, timestamp_to)
    work_days = [d for d in interval_days if d.isoweekday() <= 5]
    return work_days


def get_month_daily_salary(timestamp, month_salary):
    date = datetime.fromtimestamp(timestamp)
    first_day = date.replace(day=1)
    last_day = last_day_of_month(date)
    workdays = get_workdays_in_interval(first_day.timestamp(), last_day.timestamp())
    return math.ceil(month_salary / len(workdays))


def get_months_in_interval(timestamp_from, timestamp_to):
    dates = get_dates_from_timestamp_interval(timestamp_from, timestamp_to)
    return set([(d.month, d.year) for d in dates])


def get_sales_head_amocrm_id_list_for_all_groups(employee):
    amocrm_id_list = []
    groups_as_head = employee.groups_as_head.all()
    for group in groups_as_head:
        members = group.employee_list.all()
        amocrm_id_list += [member.amocrm_id for member in members]

    return list(set(amocrm_id_list))
