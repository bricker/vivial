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
        out: typing.IO = sys.stdout,  # TODO: should be endpoint addr instead of stdout
        formatter: typing.Callable[
            [ReadableSpan], str  # TODO: eventually replace ReadableSpan w/ our own dataclass
        ] = lambda span: span.to_json()
        + "\n",
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
