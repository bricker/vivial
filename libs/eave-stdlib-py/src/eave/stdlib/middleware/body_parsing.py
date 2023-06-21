from asgiref.typing import ASGIReceiveCallable, ASGIReceiveEvent, ASGISendCallable, Scope


from .base import EaveASGIMiddleware


class BodyParsingASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body = await self.read_body(scope=scope, receive=receive)

        async def dummy_receive() -> ASGIReceiveEvent:
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        await self.app(scope, dummy_receive, send)
