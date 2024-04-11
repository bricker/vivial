import typing
import sys
import pydantic
import asyncio
import time
import json
from opentelemetry.sdk.trace.export import SpanExportResult, SpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from eave.stdlib import requests_util
from eave.stdlib.core_api.operations import CoreApiEndpointConfiguration
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER
from eave.tracing.core.datastructures import DataIngestRequestBody, DatabaseEventPayload, DatabaseOperation, EventType

from .eave_span import EaveReadableSpan
from .async_exporter import AsyncSpanExporter

class SpanBaseModel(pydantic.BaseModel):
    events: list[str]
    event_type: EventType

def to_json(span: ReadableSpan, indent: int = 4) -> str | None:
    if not span._attributes:
        return None
    name = str(span._attributes.get("db.name"))
    op = DatabaseOperation.from_str(str(span._attributes.get("db.operation")))
 
    if op:

        f_span = DatabaseEventPayload(
            table_name=name,
            operation=op,
            parameters=None,
            timestamp=time.time(),
        ).to_dict()

        """
            -> db.statement: Str(INSERT INTO virtual_events (team_id, readable_name, description, view_id, updated) VALUES ($1::UUID, $2::VARCHAR, $3::VARCHAR, $4::VARCHAR, $5::TIMESTAMP WITHOUT TIME ZONE) RETURNING virtual_events.id, virtual_events.created)
            -> db.system: Str(postgresql)
            -> db.params: Str((UUID('5ea57c57-ed6a-4d60-b2a0-e7a605fc47be'), 'Dummy event 99.29', 'boo fuzz fazz bizz bazz fazz fizz fazz bar', '99.29', None))
            -> net.peer.name: Str(localhost)
            -> net.peer.port: Int(5432)
            -> db.name: Str(eave-test)
            -> db.user: Str(eave_db_user)
        """

        # f_span = {
        #     "name": self._name,
        #     "context": self._format_context(self._context)
        #     if self._context
        #     else None,
        #     "kind": str(self.kind),
        #     # "parent_id": parent_id,
        #     # "start_time": start_time,
        #     # "end_time": end_time,
        #     "status": status,
        #     "attributes": self._format_attributes(self._attributes),
        #     "events": self._format_events(self._events),
        #     "links": self._format_links(self._links),
        #     "resource": json.loads(self.resource.to_json()),
        # }
        return json.dumps(f_span, indent=indent)
    
    return None

class EaveSpanExporter(SpanExporter):
    """copied base from ConsoleSpanExporter
    https://github.com/open-telemetry/opentelemetry-python/blob/975733c71473cddddd0859c6fcbd2b02405f7e12/opentelemetry-sdk/src/opentelemetry/sdk/trace/export/__init__.py#L499
    """

    def __init__(
        self,
        service_name: typing.Optional[str] = None,
        out: typing.IO = sys.stdout,  # TODO: should be endpoint addr instead of stdout
        formatter: typing.Callable[
            [ReadableSpan], str  # TODO: eventually replace ReadableSpan w/ our own dataclass > cant since Readable span is all that's passed in at runtime
        ] = lambda span: span.to_json()
        + "\n",
    ):
        self.out = out
        self.formatter = formatter
        self.service_name = service_name

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        # # TODO: send to collector agent. use gRPC??
        # for span in spans:
        #     self.out.write(self.formatter(span))
        # self.out.flush()
        asyncio.run(requests_util.make_request( # TODO: dont depend on our internal stdlib; this needs to be published to public
            config=CoreApiEndpointConfiguration(
                path="/ingest",
                auth_required=False,
                team_id_required=False,
                signature_required=False,
                origin_required=False,
            ),
            input=SpanBaseModel(
                events=list(filter(None, [
                    to_json(span) for span in spans # TODO: calling our eave to_json function that is /ingest compatible causes internal err that otel eats :\
                ])),
                event_type=EventType.dbevent
            ),
            origin=EaveApp.eave_api,
            addl_headers={
                EAVE_CLIENT_ID_HEADER: "8c1f12adbf7246a9af9a09fd19a5c43a",
                EAVE_CLIENT_SECRET_HEADER: "f686f31cb4c11a9c25a526d0c7a4e58cb3e5a80959e8c55e00f528fd2af8468558ec32cfd3455b1043eb7f36ca7b024e59e40d82fe11801d48c3723ac41356ca"
            },
        ))

        return SpanExportResult.SUCCESS

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
