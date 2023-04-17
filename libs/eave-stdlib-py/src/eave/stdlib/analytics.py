import eave.pubsub_schemas.generated.eave_user_action_pb2 as eave_user_action
from google.api_core.exceptions import NotFound
from google.cloud.pubsub import PublisherClient
from google.pubsub_v1.types import Encoding

from . import logger
from .config import shared_config

publisher_client = PublisherClient()


def log_user_action(action: eave_user_action.EaveUserAction) -> None:
    topic_id = "eave_user_action"
    topic_path = publisher_client.topic_path(shared_config.google_cloud_project, topic_id)

    try:
        topic = publisher_client.get_topic(request={"topic": topic_path})
        encoding = topic.schema_settings.encoding
        assert encoding == Encoding.BINARY

        data = action.SerializeToString()
        publisher_client.publish(topic_path, data)

    except NotFound:
        logger.warn(f"{topic_id} not found.")
