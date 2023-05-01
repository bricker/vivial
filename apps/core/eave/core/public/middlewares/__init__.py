from . import asgi_types


class EaveASGIMiddleware:
    """
    https://asgi.readthedocs.io/en/latest/specs/www.html#http
    """

    app: asgi_types.ASGIFramework

    def __init__(self, app: asgi_types.ASGIFramework) -> None:
        self.app = app

    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        ...
