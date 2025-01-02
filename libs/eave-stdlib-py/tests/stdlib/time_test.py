from datetime import UTC, datetime

from eave.stdlib.time import LOS_ANGELES_TIMEZONE, datetime_window, pretty_date, pretty_datetime, pretty_time

from .base import StdlibBaseTestCase


class TestTimeHelpers(StdlibBaseTestCase):
    async def test_datetime_window(self):
        dt = datetime(2024, 12, 18, 7, 41, 22, microsecond=100)
        assert datetime_window(dt, minutes=15) == (
            datetime(2024, 12, 18, 7, 30, 0, microsecond=0),
            datetime(2024, 12, 18, 7, 44, 59, microsecond=0),
        )

        dt = datetime(2024, 12, 18, 7, 30, 22, microsecond=100)
        assert datetime_window(dt, minutes=15) == (
            datetime(2024, 12, 18, 7, 15, 0, microsecond=0),
            datetime(2024, 12, 18, 7, 44, 59, microsecond=0),
        )

        dt = datetime(2024, 12, 18, 7, 1, 22, microsecond=100)
        assert datetime_window(dt, minutes=15) == (
            datetime(2024, 12, 18, 7, 0, 0, microsecond=0),
            datetime(2024, 12, 18, 7, 14, 59, microsecond=0),
        )

        dt = datetime(2024, 12, 18, 7, 0, 22, microsecond=100)
        assert datetime_window(dt, minutes=15) == (
            datetime(2024, 12, 18, 6, 45, 0, microsecond=0),
            datetime(2024, 12, 18, 7, 14, 59, microsecond=0),
        )

    async def test_pretty_date(self):
        assert pretty_date(datetime(2025, 1, 2, 6, 27, tzinfo=LOS_ANGELES_TIMEZONE)) == "Thursday, January 2nd"
        assert pretty_date(datetime(2025, 1, 3, 6, 27, tzinfo=UTC)) == "Friday, January 3rd"

    async def test_pretty_datetime(self):
        assert (
            pretty_datetime(datetime(2025, 1, 2, 20, 27, tzinfo=LOS_ANGELES_TIMEZONE))
            == "Thursday, January 2nd at 8:27pm PST"
        )
        assert (
            pretty_datetime(datetime(2025, 1, 1, 22, 27, tzinfo=LOS_ANGELES_TIMEZONE))
            == "Wednesday, January 1st at 10:27pm PST"
        )
        assert (
            pretty_datetime(datetime(2025, 1, 1, 22, 00, tzinfo=LOS_ANGELES_TIMEZONE))
            == "Wednesday, January 1st at 10pm PST"
        )
        assert (
            pretty_datetime(datetime(2025, 1, 1, 6, 00, tzinfo=LOS_ANGELES_TIMEZONE))
            == "Wednesday, January 1st at 6am PST"
        )
        assert pretty_datetime(datetime(2025, 1, 3, 6, 27, tzinfo=UTC)) == "Friday, January 3rd at 6:27am UTC"

    async def test_pretty_time(self):
        assert pretty_time(datetime(2025, 1, 2, 6, 27, tzinfo=LOS_ANGELES_TIMEZONE)) == "6:27am"
        assert pretty_time(datetime(2025, 1, 2, 22, 27, tzinfo=LOS_ANGELES_TIMEZONE)) == "10:27pm"
        assert pretty_time(datetime(2025, 1, 2, 22, 00, tzinfo=LOS_ANGELES_TIMEZONE)) == "10:00pm"
