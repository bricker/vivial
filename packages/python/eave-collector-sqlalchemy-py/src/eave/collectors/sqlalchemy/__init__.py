from asyncio import Task, create_task
from eave.collectors.sqlalchemy.private.collector import AnyEngine, SQLAlchemyCollector
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncEngine

__collector: SQLAlchemyCollector | None = None

async def start_eave_sqlalchemy_collector(engine: AnyEngine) -> None:
    global __collector

    if not __collector:
        __collector = SQLAlchemyCollector()
        await __collector.start(engine)

def stop_eave_sqlalchemy_collector() -> None:
    global __collector

    if __collector:
        __collector.stop()

    __collector = None # Deallocate the engine.

# # TODO: try catch adding all supported instrumentation (since we dont know what deps they have). or autodetect from sys.modules
# # https://github.com/open-telemetry/opentelemetry-python-contrib/blob/7c12ad9844ac179e3f6a493491707a9bafd06f6b/opentelemetry-instrumentation/src/opentelemetry/instrumentation/bootstrap.py#L87
# def eave_instrument_server(app):
#     _init_eave_instrumentation()
#     flask.FlaskInstrumentor.instrument_app(app)
#     # starlette.StarletteInstrumentor.instrument_app(app)
#     aiohttp_client.AioHttpClientInstrumentor().instrument()

# def eave_instrument_db(engine):
#     _init_eave_instrumentation()
#     sqlalchemy_client.SQLAlchemyInstrumentor().instrument(engine=engine)
