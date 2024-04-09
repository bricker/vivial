import typing
import sys
import pydantic
import json
import asyncio
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from eave.stdlib import requests_util
from eave.stdlib.core_api.operations import CoreApiEndpointConfiguration
from eave.stdlib.eave_origins import EaveApp


# class EaveReadableSpan(ReadableSpan):
#     def to_json(self) -> typing.Any:
#         return json.dumps({})

class SpanBaseModel(pydantic.BaseModel):
    atoms: list[typing.Any]

class EaveSpanExporter(SpanExporter):
    """copied base from ConsoleSpanExporter
    https://github.com/open-telemetry/opentelemetry-python/blob/975733c71473cddddd0859c6fcbd2b02405f7e12/opentelemetry-sdk/src/opentelemetry/sdk/trace/export/__init__.py#L499
    """

    _tasks: set[asyncio.Task]

    def __init__(
        self,
        service_name: typing.Optional[str] = None,
        out: typing.IO = sys.stdout,  # TODO: should be endpoint addr instead of stdout
        formatter: typing.Callable[
            [ReadableSpan], str  # TODO: eventually replace ReadableSpan w/ our own dataclass
        ] = lambda span: span.to_json()
        + "\n",
    ):
        self.out = out
        self.formatter = formatter
        self.service_name = service_name
        self._tasks = set()


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
                atoms=[
                    span.to_json() for span in spans
                ],
            ),
            origin=EaveApp.eave_api,
        ))

        return SpanExportResult.SUCCESS

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
