import json
import typing
import uuid
import time
import eave.pubsub_schemas
from google.api_core.exceptions import NotFound
from google.cloud.pubsub import PublisherClient
from google.pubsub_v1.types import Encoding
from . import util
from . import logger
from .config import shared_config

publisher_client = PublisherClient()

# This happens to be the same between prod and dev, but could come from an environment variable if necessary.
_EVENT_TOPIC_ID = "eave_event_topic"

def log_event(
  event_name: str,
  event_description: str,
  event_source: str,
  opaque_params: typing.Optional[util.JsonObject] = None,
  eave_account_id: typing.Optional[uuid.UUID] = None,
  eave_visitor_id: typing.Optional[uuid.UUID] = None,
  eave_team_id: typing.Optional[uuid.UUID] = None,
  event_ts: typing.Optional[float] = None,
) -> None:
    event = eave.pubsub_schemas.EaveEvent(
        event_name=event_name,
        event_description=event_description,
        event_source=event_source,
        eave_account_id=str(eave_account_id) if eave_account_id else None,
        eave_visitor_id=str(eave_visitor_id) if eave_visitor_id else None,
        eave_team_id=str(eave_team_id) if eave_team_id else None,
        opaque_params=json.dumps(opaque_params) if opaque_params else None,
        event_ts=event_ts if event_ts else time.time()
    )

    topic_path = publisher_client.topic_path(shared_config.google_cloud_project, _EVENT_TOPIC_ID)

    try:
        topic = publisher_client.get_topic(request={"topic": topic_path})
        encoding = topic.schema_settings.encoding
        assert encoding == Encoding.BINARY

        data = event.SerializeToString()
        publisher_client.publish(topic_path, data)

    except NotFound:
        logger.warning(f"{_EVENT_TOPIC_ID} not found.")
