from datetime import UTC, datetime, timedelta

from eave.core.graphql.validators.time_bounds_validator import start_time_too_far_away, start_time_too_soon
from eave.stdlib.time import LOS_ANGELES_TIMEZONE

from ..base import BaseTestCase


class TestTimeBoundsValidator(BaseTestCase):
    async def test_start_time_too_soon(self) -> None:
        now = datetime.now(tz=UTC)
        assert start_time_too_soon(start_time=now + timedelta(hours=24), timezone=LOS_ANGELES_TIMEZONE) is False
        assert start_time_too_soon(start_time=now + timedelta(hours=23), timezone=LOS_ANGELES_TIMEZONE) is True
        assert start_time_too_soon(start_time=now + timedelta(hours=1), timezone=LOS_ANGELES_TIMEZONE) is True
        assert start_time_too_soon(start_time=now + timedelta(days=45), timezone=LOS_ANGELES_TIMEZONE) is False

    async def test_start_time_too_far_away(self) -> None:
        # Some of these tests may fail if you run them at 11:59:59pm... sorry!
        now = datetime.now(tz=UTC)
        assert start_time_too_far_away(start_time=now + timedelta(hours=24), timezone=LOS_ANGELES_TIMEZONE) is False
        assert start_time_too_far_away(start_time=now + timedelta(hours=1), timezone=LOS_ANGELES_TIMEZONE) is False
        assert start_time_too_far_away(start_time=now + timedelta(days=30), timezone=LOS_ANGELES_TIMEZONE) is False
        assert start_time_too_far_away(start_time=now + timedelta(days=31), timezone=LOS_ANGELES_TIMEZONE) is True
        assert start_time_too_far_away(start_time=now + timedelta(days=45), timezone=LOS_ANGELES_TIMEZONE) is True
