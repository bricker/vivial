import sqlalchemy

__collector__ = None

# def start_eave_sqlalchemy_collector(engine: sqlalchemy.Engine):
#     global __collector__

#     if not __collector__:
#         __collector__ = SQLAlchemyCollector(engine)

# def stop_eave_sqlalchemy_collector():
#     global __collector__
#     __collector__ = None

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
