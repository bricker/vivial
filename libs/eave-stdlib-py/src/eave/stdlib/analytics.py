import json
import time
import typing
import uuid

import eave.stdlib
import eave.pubsub_schemas
from google.cloud.pubsub import PublisherClient
from google.pubsub_v1.types import Encoding

from .typing import JsonObject
from .config import shared_config
from . import logging as _l

# This happens to be the same between prod and dev, but could come from an environment variable if necessary.
_EVENT_TOPIC_ID = "eave_event_topic"


def log_event(
    event_name: str,
    event_description: typing.Optional[str] = None,
    event_source: typing.Optional[str] = None,
    opaque_params: typing.Optional[JsonObject] = None,
    eave_account_id: typing.Optional[uuid.UUID | str] = None,
    eave_visitor_id: typing.Optional[uuid.UUID | str] = None,
    eave_team_id: typing.Optional[uuid.UUID | str] = None,
    event_ts: typing.Optional[float] = None,
    ctx: typing.Optional[_l.LogContext] = None,
) -> None:
    eave_context = _l.LogContext.wrap(ctx)
    opaque_params = opaque_params if opaque_params else JsonObject()
    opaque_params.setdefault("eave_ctx", eave_context)

    try:
        serialized_params = json.dumps(opaque_params)
    except Exception as e:
        _l.eaveLogger.exception(e, eave_context)
        serialized_params = str(opaque_params)

    event = eave.pubsub_schemas.EaveEvent(
        event_name=event_name,
        event_description=event_description,
        event_source=event_source,
        eave_account_id=str(eave_account_id) if eave_account_id else None,
        eave_visitor_id=str(eave_visitor_id) if eave_visitor_id else None,
        eave_team_id=str(eave_team_id) if eave_team_id else None,
        eave_env=shared_config.eave_env.value,
        opaque_params=serialized_params,
        event_ts=event_ts if event_ts else time.time(),
    )

    client = PublisherClient()

    topic_path = client.topic_path(shared_config.google_cloud_project, _EVENT_TOPIC_ID)

    topic = client.get_topic(request={"topic": topic_path})
    encoding = topic.schema_settings.encoding
    assert encoding == Encoding.BINARY, "schema encoding misconfigured"

    data = event.SerializeToString()

    if not shared_config.analytics_enabled:
        _l.eaveLogger.warning(
            "Analytics disabled.",
            eave_context,
            {"pubsub": {"event": str(data)}},
        )
    else:
        client.publish(topic_path, data)
