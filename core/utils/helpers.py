import calendar
import uuid
from decouple import config
from datetime import date, datetime, timedelta, timezone
from core.utils.date_time_converter import DateTimeConverter


def generate_registration_no():
    # Convert UUID to integer, then take the last 8 digits
    number = str(int(uuid.uuid4().int))[-8:]
    return number

def get_default_page_size(page_size=None):
    page_size = page_size or config('PAGE_SIZE', default=12)
    return int(page_size)

def default_date_time_format(input_date, format_string='%Y-%m-%d %H:%M:%S'):
    if isinstance(input_date, datetime):
        return input_date.strftime(format_string)

def default_date_format(input_date, format_string='%Y-%m-%d'):
    """
    Formats a date or datetime object into a string according to the specified format.
    """
    if isinstance(input_date, (datetime, date)):  # Use the correct type reference
        return input_date.strftime(format_string)
    return None  # Handle invalid input

from datetime import datetime, timedelta
import calendar

def get_last_months_and_days():
    today = datetime.today()

    # Get last 12 and 6 months starting from the current month
    last_12_months = [(today.year if today.month - i > 0 else today.year - 1, (today.month - i) % 12 or 12) for i in range(12)]
    last_6_months = last_12_months[:6]

    # Get last 30 and 7 days
    last_30_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
    last_7_days = last_30_days[:7]

    # Format months with year (e.g., "Feb 2024")
    formatted_months = [f"{datetime(2000, month_num, 1).strftime('%b')}-{year}" for year, month_num in last_12_months]
    formatted_months_6 = formatted_months[:6]  # Get last 6 months

    return {
        "last_12_months": list(reversed(formatted_months)),  # Reverse order to maintain chronological order
        "last_6_months": list(reversed(formatted_months_6)),  # Reverse order for 6 months
        "last_30_days": last_30_days[::-1],  # Reverse order
        "last_7_days": last_7_days[::-1]  # Reverse order
    }


def month_to_digit(month_abbr):
    try:
        return list(calendar.month_abbr).index(month_abbr.capitalize())
    except ValueError:
        return None

def get_previous_month_year(month_year):
    try:
        # Parse input string (e.g., "Apr-2024")
        date_obj = datetime.strptime(month_year, "%b-%Y")

        # Calculate the previous month
        prev_month = date_obj.month - 1
        prev_year = date_obj.year

        # If the month is January, move to December of the previous year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1

        # Format the output as "Month-Year"
        prev_month_str = datetime(prev_year, prev_month, 1).strftime("%b-%Y")
        return prev_month_str

    except ValueError:
        return None  # Handle invalid inputs gracefully


def get_previous_date(current_date: str, date_format: str = "%Y-%m-%d") -> str:
    current_date_obj = datetime.strptime(current_date, date_format)
    previous_date_obj = current_date_obj - timedelta(days=1)
    return previous_date_obj.strftime(date_format)

def check_if_user_is_staff(data):
    is_staff = data.get('auth_is_staff')
    return is_staff

def has_active_child_references(child_refs, parent_id, auth_business_id=None):
    """
    Checks if any child model has a record with the given parent_id and business_id.

    Args:
        child_refs (list): List of dicts like [{'model': SomeModel, 'foreign_key': 'parent_field_name'}]
        parent_id (int or str): The ID of the parent record.
        auth_business_id (int or str): The business ID for filtering.

    Returns:
        bool: True if any child record exists, otherwise False.
    """
    for ref in child_refs:
        model = ref['model']
        foreign_key = ref['foreign_key']

        filters = {
            foreign_key: parent_id,
        }

        if auth_business_id is not None:
            filters["business_id"] = auth_business_id

        if model.objects.filter(**filters).exists():
            return True

    return False

def calculate_date_time_difference_from_current_date_time(date_time_str, tz="UTC"):
    # convert string -> string in UTC (your converter still returns string)
    date_time_str = DateTimeConverter.to_utc_datetime(date_time_str, tz)

    # parse string into datetime object
    date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

    # make it timezone-aware (UTC)
    date_time_obj = date_time_obj.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    diff = date_time_obj - now   # works now
    hours_diff = diff.total_seconds() / 3600
    return hours_diff


def generate_hr_before_date_time(date_time_str, tz="UTC", hours=24):
    # convert to UTC datetime string using your converter
    date_time_str = DateTimeConverter.to_utc_datetime(date_time_str, tz)

    # parse into datetime object (already in UTC string)
    date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

    # subtract hours
    before_hours = date_time_obj - timedelta(hours=hours)

    # return as datetime string in UTC
    return before_hours.strftime("%Y-%m-%d %H:%M:%S")