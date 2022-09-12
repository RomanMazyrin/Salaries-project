from datetime import datetime, timedelta
import json
import math
import pytz
from amocrm_components.ApiIterator import ApiIterator
from salaries.services.SalaryCalculators.constants import AUTH_KEY, LEADS_FETCH_URL


def split_closed_leads_by_months(leads_list):
    result_map = {}
    for lead in leads_list:
        lead_closed_timestamp = lead["closed_at"]
        closed_datetime = datetime.fromtimestamp(lead_closed_timestamp)
        lead_closed_month_key = (closed_datetime.month, closed_datetime.year)
        if not result_map.get(lead_closed_month_key):
            result_map[lead_closed_month_key] = []
        result_map[lead_closed_month_key].append(lead)
    return result_map


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def fetch_all_amocrm_entities_by_filter(**kwargs):
    f = ApiIterator(**kwargs)
    entities = []
    for entity in f.get_next():
        entities.append(entity)
    return entities


def fetch_all_leads_by_months_covered_by_timestamp_interval(
    timestamp_from, timestamp_to, user_id=None, statuses=None
):

    timezone = pytz.timezone("Europe/Moscow")

    left_timestamp_border = (
        datetime.fromtimestamp(timestamp_from, timezone)
        .replace(day=1, hour=0, minute=0, second=0)
        .timestamp()
    )
    right_timestamp_border = (
        datetime.fromtimestamp(timestamp_to).replace(hour=23, minute=59, second=59).timestamp()
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
