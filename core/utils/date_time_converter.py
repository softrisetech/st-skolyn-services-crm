from datetime import datetime
import pytz
from dateutil import parser
from datetime import time

class DateTimeConverter:
    @staticmethod
    def to_utc_datetime(date_time_str, from_zone, date_time_format='%Y-%m-%d %H:%M:%S'):
        local_tz = pytz.timezone(from_zone)
        local_dt = datetime.strptime(date_time_str, date_time_format)
        localized_dt = local_tz.localize(local_dt)
        utc_dt = localized_dt.astimezone(pytz.utc)
        return utc_dt.strftime(date_time_format)

    @staticmethod
    def from_utc_datetime(date_time_str, to_zone, date_time_format='%Y-%m-%d %H:%M:%S'):
        """
        Converts an ISO 8601 UTC string like '2025-04-07T11:11:15.816271Z'
        to local time formatted as a string.
        """
        utc_dt = parser.isoparse(date_time_str).astimezone(pytz.timezone(to_zone))
        return utc_dt.strftime(date_time_format)

    @staticmethod
    def to_utc_date(date_str, from_zone, date_format='%Y-%m-%d'):
        local_tz = pytz.timezone(from_zone)
        current_time_str = datetime.now(local_tz).strftime('%H:%M:%S')
        full_datetime_str = f"{date_str} {current_time_str}"
        local_dt = datetime.strptime(full_datetime_str, '%Y-%m-%d %H:%M:%S')
        localized_dt = local_tz.localize(local_dt)
        utc_dt = localized_dt.astimezone(pytz.utc)
        return utc_dt.strftime(date_format)

    @staticmethod
    def from_utc_date(date_str, to_zone, date_format='%Y-%m-%d'):
        utc_now = datetime.utcnow().strftime('%H:%M:%S')
        full_datetime_str = f"{date_str} {utc_now}"
        utc_dt = datetime.strptime(full_datetime_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
        target_dt = utc_dt.astimezone(pytz.timezone(to_zone))
        return target_dt.strftime(date_format)

    @staticmethod
    def to_utc_time(time_str, from_zone, time_format='%H:%M:%S'):
        local_tz = pytz.timezone(from_zone)
        today_str = datetime.now(local_tz).strftime('%Y-%m-%d')
        full_datetime_str = f"{today_str} {time_str}"
        local_dt = datetime.strptime(full_datetime_str, '%Y-%m-%d %H:%M:%S')
        localized_dt = local_tz.localize(local_dt)
        utc_dt = localized_dt.astimezone(pytz.utc)
        return utc_dt.strftime(time_format)

    @staticmethod
    def from_utc_time(time_str, to_zone, time_format='%H:%M:%S'):
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        full_datetime_str = f"{today_str} {time_str}"
        utc_dt = datetime.strptime(full_datetime_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
        target_dt = utc_dt.astimezone(pytz.timezone(to_zone))
        return target_dt.strftime(time_format)

    @staticmethod
    def to_utc_range(date_str, from_zone, is_end=False):
        local_tz = pytz.timezone(from_zone)

        dt = datetime.strptime(date_str, "%Y-%m-%d")

        if is_end:
            dt = datetime.combine(dt, time.max)
        else:
            dt = datetime.combine(dt, time.min)

        localized_dt = local_tz.localize(dt)
        utc_dt = localized_dt.astimezone(pytz.utc)

        return utc_dt