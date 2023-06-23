from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope

from eave.stdlib.request_state import EaveRequestState

from ..logging import eaveLogger

from .base import EaveASGIMiddleware


class LoggingASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        eave_state = EaveRequestState.load(scope=scope)
        eaveLogger.info(
            f"Request Start: {eave_state.ctx.eave_request_id}: {scope['method']} {scope['path']}",
            eave_state.ctx,
        )
        await self.app(scope, receive, send)
        eaveLogger.info(
            f"Request End: {eave_state.ctx.eave_request_id}: {scope['method']} {scope['path']}",
            eave_state.ctx,
        )
