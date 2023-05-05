import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

from google.api_core.exceptions import AlreadyExists
from google.cloud.pubsub import SchemaServiceClient
from google.pubsub_v1.types import Schema


class Environment:
    GCLOUD_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]


project_path = f"projects/{Environment.GCLOUD_PROJECT}"
schema_client = SchemaServiceClient()


class DuplicateSchemaIdError(Exception):
    def __init__(self, schema_id: str):
        msg = f"Duplicate schema ID: {schema_id}"
        super().__init__(msg)


class SchemaDiscrepancyError(Exception):
    def __init__(self, schema_id: str):
        msg = (
            f"Schema {schema_id} already exists in remote and does not match local schema. "
            "Schemas cannot be changed once published! "
            "Consider duplicating the schema."
        )

        super().__init__(msg)


def load_remote_schemas() -> dict[str, str]:
    remote_schemas = schema_client.list_schemas(parent=project_path)

    # schema_id -> definition
    definitions = dict[str, str]()
    for schema_info in remote_schemas:
        schema = schema_client.get_schema(name=schema_info.name)
        schema_id = schema_client.parse_schema_path(schema.name)["schema"]
        definitions[schema_id] = schema.definition

    return definitions


def load_local_schemas() -> dict[str, str]:
    # schema_id -> definition
    schemas = dict[str, str]()

    for dirpath, _, filenames in os.walk("protos"):
        for f in filenames:
            (schema_id, ext) = os.path.splitext(f)
            if ext != ".proto":
                continue

            if schemas.get(schema_id) is not None:
                raise DuplicateSchemaIdError(schema_id)

            filepath = os.path.join(dirpath, f)
            with open(filepath, "rb") as fd:
                definition = fd.read().decode("utf-8")

            schemas[schema_id] = definition

    return schemas


def publish_schema(schema_id: str, schema_definition: str) -> None:
    schema_path = schema_client.schema_path(Environment.GCLOUD_PROJECT, schema_id)
    schema = Schema(
        name=schema_path,
        type_=Schema.Type.PROTOCOL_BUFFER,
        definition=schema_definition,
    )

    try:
        schema_client.create_schema(
            request={"parent": project_path, "schema": schema, "schema_id": schema_id},
        )

        logging.info(f"Schema {schema_id} published to remote.")
    except AlreadyExists:
        logging.info(f"Schema {schema_id} already exists on remote. This is normal. Skipping.")


def create_topic() -> None:
    pass


def create_subscription() -> None:
    pass


def run() -> None:
    print("run")
    remote_schemas = load_remote_schemas()
    local_schemas = load_local_schemas()

    for schema_id in local_schemas.keys():
        local_definition = local_schemas[schema_id]

        remote_definition = remote_schemas.get(schema_id)
        if remote_definition is not None:
            if local_definition != remote_definition:
                raise SchemaDiscrepancyError(schema_id)

            logging.info(f"Schema {schema_id} already exists on remote. This is normal. Skipping.")
            continue

        publish_schema(schema_id, local_definition)


if __name__ == "__main__":
    run()
