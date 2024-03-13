import asgiref.typing


from .base import EaveASGIMiddleware


class BodyParsingASGIMiddleware(EaveASGIMiddleware):
    async def run(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body = await self.read_body(scope=scope, receive=receive)

        async def dummy_receive() -> asgiref.typing.ASGIReceiveEvent:
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        await self.app(scope, dummy_receive, send)
