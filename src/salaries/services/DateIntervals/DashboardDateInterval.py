from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class DashboardDateInterval(ABC):

    BASIC_DATE_FORMAT = "%d.%m.%Y"

    def __init__(self, date_from=None, date_to=None, *args, **kwargs):
        self.date_from = date_from
        self.date_to = date_to

    def create_datetime(self, date_str):
        if not date_str or date_str == "false":
            dt = datetime()
        else:
            dt = datetime.strptime(date_str, self.BASIC_DATE_FORMAT)
        return dt

    @abstractmethod
    def get_timestamp_from(self):
        pass

    @abstractmethod
    def get_timestamp_to(self):
        pass


class CustomInterval(DashboardDateInterval):
    def get_timestamp_from(self):
        dt = self.create_datetime(self.date_from)
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return dt.timestamp()

    def get_timestamp_to(self):
        dt = self.create_datetime(self.date_to)
        dt = dt.replace(hour=23, minute=59, second=59, microsecond=0)
        return dt.timestamp()


class DayInterval(DashboardDateInterval):
    def get_timestamp_from(self):
        dt = datetime.now()
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return dt.timestamp()

    def get_timestamp_to(self):
        dt = datetime.now()
        dt = dt.replace(hour=23, minute=59, second=59, microsecond=0)
        return dt.timestamp()


class MonthInterval(DashboardDateInterval):
    def get_timestamp_from(self):
        dt = datetime.now()
        dt = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return dt.timestamp()

    def get_timestamp_to(self):
        dt = datetime.now()
        return dt.replace(microsecond=0).timestamp()


class WeekInterval(DashboardDateInterval):
    def get_timestamp_from(self):
        dt = datetime.now()
        delta = timedelta(7)
        result = dt - delta
        return result.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    def get_timestamp_to(self):
        dt = datetime.now()
        return dt.replace(microsecond=0).timestamp()


class YesterdayInterval(DashboardDateInterval):
    def __get_yesterday(self):
        return datetime.now() - timedelta(1)

    def get_timestamp_from(self):
        dt = self.__get_yesterday()
        return dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    def get_timestamp_to(self):
        dt = self.__get_yesterday()
        return dt.replace(hour=23, minute=59, second=59, microsecond=0).timestamp()


intervals = {
    "month": MonthInterval,
    "yesterday": YesterdayInterval,
    "week": WeekInterval,
    "day": DayInterval,
    "custom": CustomInterval,
}


def create_interval(**kwargs):
    interval_name = kwargs.get("period", "month")
    interval_class = intervals[interval_name]
    return interval_class(**kwargs)
