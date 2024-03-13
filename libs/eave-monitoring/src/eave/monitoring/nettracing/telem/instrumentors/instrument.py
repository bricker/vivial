# from opentelemetry.instrumentation.flask import FlaskInstrumentor
# from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry.trace import get_tracer_provider, set_tracer_provider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from eave.monitoring.nettracing.telem.instrumentors import flask, aiohttp_client


# TODO: try catch adding all supported instrumentation (since we dont know what deps they have). or autodetect from sys.modules
# https://github.com/open-telemetry/opentelemetry-python-contrib/blob/7c12ad9844ac179e3f6a493491707a9bafd06f6b/opentelemetry-instrumentation/src/opentelemetry/instrumentation/bootstrap.py#L87
def eave_instrument(app):
    set_tracer_provider(TracerProvider())
    get_tracer_provider().add_span_processor(  # type: ignore
        BatchSpanProcessor(OTLPSpanExporter(endpoint="http://0.0.0.0:4317"))  # EaveSpanExporter())
    )
    flask.FlaskInstrumentor.instrument_app(app)
    # starlette.StarletteInstrumentor.instrument_app(app)
    aiohttp_client.AioHttpClientInstrumentor().instrument()
