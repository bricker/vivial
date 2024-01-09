"""
so are we going to basically end up writing our own open telem api interface impl??

curernt open telem impls predictably only capture url and http method

i think well need to fork every opentelem instrumetation rerpo we care about, alter code to gather req/resp body data, bundle our fork w/ the opentelem api, and then release for customers
(unsure if there is a 1 LOC solution for opentelem; current demo was wrapping the executable)
"""
import typing
import sys
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

class EaveSpanExporter(SpanExporter):
    """copied base from ConsoleSpanExporter
    https://github.com/open-telemetry/opentelemetry-python/blob/975733c71473cddddd0859c6fcbd2b02405f7e12/opentelemetry-sdk/src/opentelemetry/sdk/trace/export/__init__.py#L499
    """

    def __init__(
        self,
        service_name: typing.Optional[str] = None,
        out: typing.IO = sys.stdout, # TODO: should be endpoint addr instead of stdout
        formatter: typing.Callable[
            [ReadableSpan], str # TODO: eventually replace ReadableSpan w/ our own dataclass
        ] = lambda span: span.to_json()
        + '\n',
    ):
        self.out = out
        self.formatter = formatter
        self.service_name = service_name

    def export(self, spans: typing.Sequence[ReadableSpan]) -> SpanExportResult:
        # TODO: send to collector agent. use gRPC??
        for span in spans:
            self.out.write(self.formatter(span))
        self.out.flush()
        return SpanExportResult.SUCCESS

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True
