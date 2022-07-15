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