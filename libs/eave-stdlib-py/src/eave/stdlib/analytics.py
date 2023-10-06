from datetime import datetime
import json
import typing
from uuid import UUID

from google.pubsub_v1 import PublisherAsyncClient, PubsubMessage
from eave.pubsub_schemas import EaveEvent, GPTRequestEvent

from eave.stdlib.core_api.models.account import AnalyticsAccount

from eave.stdlib.core_api.models.team import AnalyticsTeam

from .typing import JsonObject
from .config import shared_config
from . import logging as _l

# This happens to be the same between prod and dev, but could come from an environment variable if necessary.
_EVENT_TOPIC_ID = "eave_event"
_GPT_EVENT_TOPIC_ID = "gpt_request_event"


async def log_event(
    event_name: str,
    ctx: typing.Optional[_l.LogContext],
    event_description: typing.Optional[str] = None,
    event_source: typing.Optional[str] = None,
    opaque_params: typing.Optional[JsonObject] = None,
    eave_account: typing.Optional[AnalyticsAccount] = None,
    eave_team: typing.Optional[AnalyticsTeam] = None,
) -> None:
    serialized_account = eave_account.json() if eave_account else None
    serialized_team = eave_team.json() if eave_team else None
    serialized_params = _safe_serialize(opaque_params, ctx)
    serialized_context = _safe_serialize(ctx, ctx)

    event_time = datetime.utcnow().isoformat()

    eave_account_id: str | UUID | None = None
    eave_visitor_id: str | UUID | None = None

    if eave_account:
        eave_account_id = eave_account.id
        eave_visitor_id = eave_account.visitor_id
    elif ctx:
        eave_account_id = ctx.eave_account_id

    if not eave_visitor_id and ctx:
        eave_visitor_id = ctx.eave_visitor_id

    eave_team_id: str | UUID | None = None
    if eave_team:
        eave_team_id = eave_team.id
    elif ctx:
        eave_team_id = ctx.eave_team_id

    event = EaveEvent(
        event_name=event_name,
        event_description=event_description,
        event_time=event_time,
        event_source=event_source,
        eave_account_id=str(eave_account_id) if eave_account_id else None,
        eave_visitor_id=str(eave_visitor_id) if eave_visitor_id else None,
        eave_team_id=str(eave_team_id) if eave_team_id else None,
        eave_env=shared_config.eave_env.value,
        opaque_params=serialized_params,
        opaque_eave_ctx=serialized_context,
        eave_account=serialized_account,
        eave_team=serialized_team,
        eave_request_id=ctx.eave_request_id if ctx else None,
    )

    await _send_event(event, _EVENT_TOPIC_ID, ctx)


async def log_gpt_request(
    duration_seconds: int,
    input_cost_usd: float,
    output_cost_usd: float,
    input_prompt: str,
    output_response: str,
    input_token_count: int,
    output_token_count: int,
    model: str,
    ctx: typing.Optional[_l.LogContext],
    document_id: typing.Optional[str],
) -> None:
    event_time = datetime.utcnow().isoformat()

    event = GPTRequestEvent(
        feature_name=ctx.feature_name if ctx else None,
        event_time=event_time,
        duration_seconds=duration_seconds,
        eave_request_id=ctx.eave_request_id if ctx else None,
        input_cost_usd=input_cost_usd,
        output_cost_usd=output_cost_usd,
        input_prompt=input_prompt,
        output_response=output_response,
        input_token_count=input_token_count,
        output_token_count=output_token_count,
        model=model,
        eave_team_id=ctx.eave_team_id if ctx else "null",  # for consistency with TS code
        document_id=document_id,
    )

    await _send_event(event, _GPT_EVENT_TOPIC_ID, ctx)


async def _send_event(event: typing.Any, topic_id: str, ctx: typing.Optional[_l.LogContext] = None) -> None:
    """
    This must be initialized _per message_ when using asyncio (as opposed to once per process at the top of the module),
    otherwise errors due to futures attached to separate loops.
    """
    client = PublisherAsyncClient()
    topic_path = client.topic_path(shared_config.google_cloud_project, topic_id)
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

        try:
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
        except Exception as e:
            _l.eaveLogger.exception(e, {"pubsub": {"event": str(event)}}, ctx)


def _safe_serialize(data: JsonObject | None, ctx: _l.LogContext | None) -> str | None:
    if not data:
        return None

    try:
        serialized_params = json.dumps(data)
    except Exception as e:
        _l.eaveLogger.exception(e, ctx)
        serialized_params = str(data)

    return serialized_params
