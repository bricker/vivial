from eave.stdlib.typing import JsonObject
import segment.analytics

from eave.core.internal.config import CORE_API_APP_CONFIG


class AnalyticsTracker:
    def __init__(self) -> None:
        segment.analytics.write_key = CORE_API_APP_CONFIG.segment_write_key

        if CORE_API_APP_CONFIG.is_dev_env:
            segment.analytics.debug = True
            segment.analytics.on_error = lambda error, _: print("Segment analytics error:", error)
            # dont deliver analytics events to segment in dev mode
            segment.analytics.send = False

    def identify(self, user_id: str, extra_properties: JsonObject) -> None:
        segment.analytics.identify(user_id, extra_properties)


ANALYTICS = AnalyticsTracker()
