from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

def due_date(days_ahead):
    """Returns a datetime for a due date a set number of days in the future.
    Uses settings.DUE_DATE_HOUR for a consistent due date hour. If the current 
    hour is past settings.DUE_DATE_HOUR, gives an extra day.
    """
    if timezone.now().hour >= settings.DUE_DATE_HOUR:
        days = settings.DAYS_TO_REVIEW + 1
    else:
        days = settings.DAYS_TO_REVIEW
    due_date = (timezone.now() + timedelta(days=days_ahead))
    due_date = due_date.replace(hour=settings.DUE_DATE_HOUR, minute=0, second=0)
    return due_date
