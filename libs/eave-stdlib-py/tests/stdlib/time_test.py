from datetime import datetime

from eave.stdlib.time import datetime_window

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
