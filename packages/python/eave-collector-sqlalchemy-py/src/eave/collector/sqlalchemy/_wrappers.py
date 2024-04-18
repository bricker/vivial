def _wrap_create_async_engine(tracer, connections_usage, enable_commenter=False, commenter_options=None):
    def _wrap_create_async_engine_internal(func, module, args, kwargs):
        """Trace the SQLAlchemy engine, creating an `EngineTracer`
        object that will listen to SQLAlchemy events.
        """
        engine = func(*args, **kwargs)
        EngineTracer(
            tracer,
            engine.sync_engine,
            connections_usage,
            enable_commenter,
            commenter_options,
        )
        return engine

    return _wrap_create_async_engine_internal


def _wrap_create_engine(tracer, connections_usage, enable_commenter=False, commenter_options=None):
    def _wrap_create_engine_internal(func, _module, args, kwargs):
        """Trace the SQLAlchemy engine, creating an `EngineTracer`
        object that will listen to SQLAlchemy events.
        """
        engine = func(*args, **kwargs)
        EngineTracer(
            tracer,
            engine,
            connections_usage,
            enable_commenter,
            commenter_options,
        )
        return engine

    return _wrap_create_engine_internal


def _wrap_connect(tracer):
    # pylint: disable=unused-argument
    def _wrap_connect_internal(func, module, args, kwargs):
        with tracer.start_as_current_span("connect", kind=trace.SpanKind.CLIENT) as span:
            if span.is_recording():
                attrs, _ = _get_attributes_from_url(module.url)
                span.set_attributes(attrs)
                span.set_attribute(SpanAttributes.DB_SYSTEM, _normalize_vendor(module.name))
            return func(*args, **kwargs)

    return _wrap_connect_internal


def wrap_sqlalchemy():
    _w(
        "sqlalchemy",
        "create_engine",
        _wrap_create_engine(tracer, connections_usage, enable_commenter, commenter_options),
    )
    _w(
        "sqlalchemy.engine",
        "create_engine",
        _wrap_create_engine(tracer, connections_usage, enable_commenter, commenter_options),
    )
    _w(
        "sqlalchemy.engine.base",
        "Engine.connect",
        _wrap_connect(tracer),
    )
    if parse_version(sqlalchemy.__version__).release >= (1, 4):
        _w(
            "sqlalchemy.ext.asyncio",
            "create_async_engine",
            _wrap_create_async_engine(
                tracer,
                connections_usage,
                enable_commenter,
                commenter_options,
            ),
        )
    if kwargs.get("engine") is not None:
        return EngineTracer(
            tracer,
            kwargs.get("engine"),
            connections_usage,
            kwargs.get("enable_commenter", False),
            kwargs.get("commenter_options", {}),
        )
    if kwargs.get("engines") is not None and isinstance(kwargs.get("engines"), Sequence):
        return [
            EngineTracer(
                tracer,
                engine,
                connections_usage,
                kwargs.get("enable_commenter", False),
                kwargs.get("commenter_options", {}),
            )
            for engine in kwargs.get("engines", [])
        ]

    return None


def unwrap_sqlalchemy():
    unwrap(sqlalchemy, "create_engine")
    unwrap(sqlalchemy.engine, "create_engine")
    unwrap(Engine, "connect")
    if parse_version(sqlalchemy.__version__).release >= (1, 4):
        unwrap(sqlalchemy.ext.asyncio, "create_async_engine")
    EngineTracer.remove_all_event_listeners()
