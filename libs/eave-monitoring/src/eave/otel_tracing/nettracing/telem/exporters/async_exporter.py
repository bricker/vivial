import typing
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan

class AsyncSpanExporter:
    """Interface for exporting spans.

    Interface to be implemented by services that want to export spans recorded
    in their own format.

    To export data this MUST be registered to the :class`opentelemetry.sdk.trace.Tracer` using a
    `SimpleSpanProcessor` or a `BatchSpanProcessor`.
    """

    async def export(
        self, spans: typing.Sequence[ReadableSpan]
    ) -> "SpanExportResult":
        """Exports a batch of telemetry data.

        Args:
            spans: The list of `opentelemetry.trace.Span` objects to be exported

        Returns:
            The result of the export
        """
        ...

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        ...

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Hint to ensure that the export of any spans the exporter has received
        prior to the call to ForceFlush SHOULD be completed as soon as possible, preferably
        before returning from this method.
        """
        ...