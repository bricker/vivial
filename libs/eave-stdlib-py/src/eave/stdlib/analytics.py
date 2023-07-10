from datetime import datetime
import json
import typing

from google.pubsub_v1 import PublisherAsyncClient, PubsubMessage
from eave.pubsub_schemas import EaveEvent

from eave.stdlib.core_api.models.account import AnalyticsAccount

from eave.stdlib.core_api.models.team import AnalyticsTeam

from .typing import JsonObject
from .config import shared_config
from . import logging as _l

# This happens to be the same between prod and dev, but could come from an environment variable if necessary.
_EVENT_TOPIC_ID = "eave_event"



async def log_event(
    event_name: str,
    event_description: typing.Optional[str] = None,
    event_source: typing.Optional[str] = None,
    opaque_params: typing.Optional[JsonObject] = None,
    eave_account: typing.Optional[AnalyticsAccount] = None,
    eave_team: typing.Optional[AnalyticsTeam] = None,
    ctx: typing.Optional[_l.LogContext] = None,
) -> None:
    serialized_account = eave_account.json() if eave_account else None
    serialized_team = eave_team.json() if eave_team else None
    serialized_params = _safe_serialize(opaque_params, ctx)
    serialized_context = _safe_serialize(ctx, ctx)

    event_time = datetime.utcnow().isoformat()

    event = EaveEvent(
        event_name=event_name,
        event_description=event_description,
        event_time=event_time,
        event_source=event_source,
        eave_account_id=str(eave_account.id) if eave_account else None,
        eave_visitor_id=str(eave_account.visitor_id) if eave_account else None,
        eave_team_id=str(eave_team.id) if eave_team else None,
        eave_env=shared_config.eave_env.value,
        opaque_params=serialized_params,
        opaque_eave_ctx=serialized_context,
        eave_account=serialized_account,
        eave_team=serialized_team,
    )

    # This must be initialized _per message_ when using asyncio (as opposed to once per process at the top of the module), otherwise errors due to futures attached to separate loops.
    client = PublisherAsyncClient()
    topic_path = client.topic_path(shared_config.google_cloud_project, _EVENT_TOPIC_ID)
    data = event.SerializeToString()

    if not shared_config.analytics_enabled:
        _l.eaveLogger.warning(
            "Analytics disabled.",
            ctx,
            {"pubsub": {"event": str(event)}},
        )
    else:
        _l.eaveLogger.debug(
            "Publishing analytics event",
            ctx,
            {"pubsub": {"event": str(event)}},
        )

        result = await client.publish(topic=topic_path, messages=[PubsubMessage(data=data)])

        _l.eaveLogger.debug(
            "Analytics event published",
            ctx,
            {
                "pubsub": {
                    "event": str(event),
                    "result": list(result.message_ids),
                }
            },
        )


def _safe_serialize(data: JsonObject | None, ctx: _l.LogContext | None) -> str | None:
    if not data:
        return None

    try:
        serialized_params = json.dumps(data)
    except Exception as e:
        _l.eaveLogger.exception(e, ctx)
        serialized_params = str(data)

    return serialized_params
