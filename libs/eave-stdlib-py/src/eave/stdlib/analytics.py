import logging
from typing import TypedDict
from uuid import UUID

import segment.analytics

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonObject

SEGMENT_ANONYMOUS_ID_COOKIE_NAME = "ajs_anonymous_id"
SEGMENT_USER_ID_COOKIE_NAME = "ajs_user_id"


class AnalyticsContext(TypedDict):
    authenticated_account_id: str | None
    visitor_id: str | None
    correlation_id: str | None
    client_geo: JsonObject | None
    client_ip: str | None


class AnalyticsTracker:
    def __init__(self, write_key: str) -> None:
        segment.analytics.write_key = write_key
        segment.analytics.debug = SHARED_CONFIG.log_level == logging.DEBUG

        # dont deliver analytics events to segment in dev mode
        segment.analytics.send = SHARED_CONFIG.analytics_enabled

        if not SHARED_CONFIG.analytics_enabled:
            segment.analytics.on_error = lambda error, _: LOGGER.exception("Segment analytics error:", error)

    def identify(
        self,
        *,
        account_id: UUID,
        visitor_id: str | None,
        extra_properties: JsonObject | None = None,
    ) -> None:
        """Identify a user.
        Should only be called on account creation, or update.
        https://segment.com/docs/connections/sources/catalog/libraries/server/python/#identify
        """
        segment.analytics.identify(
            user_id=str(account_id),
            traits=extra_properties,
            anonymous_id=visitor_id,
        )

    def track(
        self,
        *,
        event_name: str,
        account_id: UUID | None,
        visitor_id: str | None,
        ctx: AnalyticsContext | None,
        extra_properties: JsonObject | None = None,
    ) -> None:
        """Track a user triggered action.
        At least one of `user_id` or `visitor_id` must be provided.
        https://segment.com/docs/connections/sources/catalog/libraries/server/python/#track
        """

        # TODO: What values to pass if account_id and visitor_id are null?
        user_id = str(account_id or "")
        anon_id = visitor_id or ""

        properties = {}
        if extra_properties:
            properties.update(extra_properties)
        if ctx:
            properties.update(ctx)

        segment.analytics.track(
            user_id=user_id,
            event=event_name,
            properties=properties,
            anonymous_id=anon_id,
        )
