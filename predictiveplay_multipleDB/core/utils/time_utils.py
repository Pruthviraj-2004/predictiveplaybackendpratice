import pytz
from datetime import datetime
from django.utils import timezone


def is_prediction_closed(match):
    """
    Returns True if current IST time is >= match start time
    """

    ist = pytz.timezone("Asia/Kolkata")

    match_datetime = datetime.combine(
        match.match_date,
        match.match_time
    )

    match_datetime_ist = ist.localize(match_datetime)

    current_time_ist = timezone.now().astimezone(ist)

    return current_time_ist >= match_datetime_ist