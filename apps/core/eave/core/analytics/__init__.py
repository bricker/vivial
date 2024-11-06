import segment.analytics

from eave.core.internal.config import CORE_API_APP_CONFIG

segment.analytics.write_key = CORE_API_APP_CONFIG.segment_write_key
