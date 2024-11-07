from uuid import UUID
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

    def identify(self, account_id: UUID, extra_properties: JsonObject | None = None) -> None:
        """Identify a user.
        Should only be called on account creation, or update.
        https://segment.com/docs/connections/sources/catalog/libraries/server/python/#identify
        """
        segment.analytics.identify(user_id=str(account_id), traits=extra_properties)

    def track(
        self,
        event_name: str,
        account_id: UUID | None = None,
        visitor_id: UUID | None = None,
        extra_properties: JsonObject | None = None,
    ) -> None:
        """Track a user triggered action.
        At least one of `user_id` or `visitor_id` must be provided.
        https://segment.com/docs/connections/sources/catalog/libraries/server/python/#track
        """
        assert account_id or visitor_id, "At least one of `user_id` or `visitor_id` must be provided"
        user_id = str(account_id) if account_id else None
        anon_id = str(visitor_id) if visitor_id else None
        segment.analytics.track(
            user_id=user_id,
            event=event_name,
            properties=extra_properties,
            anonymous_id=anon_id,
        )

    def alias(self, visitor_id: UUID, account_id: UUID) -> None:
        """Associate a Segment identity with another one.
        Required for Mixpanel to be able to associate users with their actions prior to account creation.
        https://segment.com/docs/connections/sources/catalog/libraries/server/python/#alias
        """
        segment.analytics.alias(previous_id=str(visitor_id), user_id=str(account_id))


ANALYTICS = AnalyticsTracker()
