
from datetime import datetime, timedelta
import pytz

def central_offset():
    central = datetime.now(pytz.timezone('US/Central'))
    return abs(int(central.utcoffset().total_seconds()/60/60))

def start_of_day(current=None):
    current = current or datetime.now()
    central = current - timedelta(hours=central_offset())
    return datetime(central.year, central.month, central.day, central_offset(), 0)

def end_of_day(current=None):
    current = current or datetime.now()
    return start_of_day(current) + timedelta(days=1)

def is_weekday(date):
    weekend = ['Sat', 'Sun']
    return date.strftime('%a') not in weekend