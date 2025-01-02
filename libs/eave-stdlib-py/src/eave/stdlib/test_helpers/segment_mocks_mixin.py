import unittest.mock
from typing import Any, override

from eave.stdlib.test_helpers.mocking_mixin import MockingMixin


class SegmentMocksMixin(MockingMixin):
    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._add_segment_client_mocks()

    def _add_segment_client_mocks(self) -> None:
        def _mocked_segment_track(*args, **kwargs) -> Any:
            pass

        self.patch(
            name="segment.analytics.track",
            patch=unittest.mock.patch("segment.analytics.track"),
            side_effect=_mocked_segment_track,
        )

        def _mocked_segment_identify(*args, **kwargs) -> Any:
            pass

        self.patch(
            name="segment.analytics.identify",
            patch=unittest.mock.patch("segment.analytics.identify"),
            side_effect=_mocked_segment_identify,
        )
