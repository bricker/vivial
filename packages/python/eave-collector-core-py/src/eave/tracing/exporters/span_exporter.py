# import typing
# import sys
# import pydantic
# import asyncio
# import time
# import json
# from opentelemetry.sdk.trace.export import SpanExportResult, SpanExporter
# from opentelemetry.sdk.trace import ReadableSpan
# from opentelemetry.semconv.trace import SpanAttributes
# from eave.otel_tracing.nettracing.telem.config.config_reader import EaveConfigReader
# from eave.stdlib import requests_util
# from eave.stdlib.core_api.operations import CoreApiEndpointConfiguration
# from eave.stdlib.eave_origins import EaveApp
# from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER
# from eave.tracing.core.datastructures import DataIngestRequestBody, DatabaseEventPayload, DatabaseOperation, DatabaseStructure, EventType

# # TODO: move this stuff to share w/ instrumentors
# DB_PARAMS = "db.params.values"
# DB_STRUCTURE = "db.structure"
# class SpanBaseModel(pydantic.BaseModel):
#     events: list[str]
#     event_type: EventType

# def to_json(span: ReadableSpan, indent: int = 4) -> str | None:
#     if not span._attributes:
#         return None

#     # TODO: add new attrs to the paylaod
#     statement = str(span._attributes.get(SpanAttributes.DB_STATEMENT))
#     params = typing.cast(list[str] | None, span._attributes.get(DB_PARAMS))
#     struct = DatabaseStructure.from_str(str(span._attributes.get(DB_STRUCTURE))) or DatabaseStructure.UNKNOWN

#     f_span = DatabaseEventPayload(
#         statement=statement,
#         parameters=params,
#         timestamp=time.time(),
#         db_structure=struct,
#     ).to_dict()

#     return json.dumps(f_span, indent=indent)


# class EaveSpanExporter(SpanExporter):
#     """copied base from ConsoleSpanExporter
#     https://github.com/open-telemetry/opentelemetry-python/blob/975733c71473cddddd0859c6fcbd2b02405f7e12/opentelemetry-sdk/src/opentelemetry/sdk/trace/export/__init__.py#L499
#     """

#     def __init__(self):
#         super().__init__()
#         self.config = EaveConfigReader()

#     def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
#         asyncio.run(requests_util.make_request( # TODO: dont depend on our internal stdlib; this needs to be published to public
#             config=CoreApiEndpointConfiguration(
#                 path="/ingest",
#                 auth_required=False,
#                 team_id_required=False,
#                 signature_required=False,
#                 origin_required=False,
#             ),
#             input=SpanBaseModel(
#                 events=list(filter(None, [
#                     to_json(span) for span in spans
#                 ])),
#                 event_type=EventType.dbevent
#             ),
#             origin=EaveApp.eave_api,
#             addl_headers={
#                 EAVE_CLIENT_ID_HEADER: self.config.client_id,
#                 EAVE_CLIENT_SECRET_HEADER: self.config.client_secret,
#             },
#         ))

#         return SpanExportResult.SUCCESS

#     def force_flush(self, timeout_millis: int = 30000) -> bool:
#         return True
