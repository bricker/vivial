from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.stdlib.analytics import AnalyticsTracker

ANALYTICS = AnalyticsTracker(write_key=CORE_API_APP_CONFIG.segment_write_key)
