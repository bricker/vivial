from datetime import datetime, timedelta


class StartTimeTooSoonError(Exception):
    pass


class StartTimeTooLateError(Exception):
    pass


def validate_time_within_bounds_or_exception(start_time: datetime) -> None:
    """Ensure an event start time is within the bounds of when
    we can safely book events for a user."""
    now = datetime.now()
    if start_time - now > timedelta(days=30):
        raise StartTimeTooLateError()
    if start_time - now < timedelta(hours=24):
        raise StartTimeTooSoonError()
