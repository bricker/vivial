from eave.core.config import CORE_API_APP_CONFIG
from eave.stdlib.analytics import AnalyticsTracker
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER

try:
    _tracker = AnalyticsTracker(write_key=CORE_API_APP_CONFIG.segment_write_key)
except KeyError as e:
    if not SHARED_CONFIG.analytics_enabled:
        LOGGER.exception(e)
        LOGGER.warning("Segment API key not set! Analytics won't be sent.")
        _tracker = AnalyticsTracker(write_key="")
    else:
        # This makes sure that the pod won't start in Kubernetes.
        raise

ANALYTICS = _tracker
