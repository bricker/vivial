import eave.stdlib
import eave.core.public
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope

from . import EaveASGIMiddleware


class LoggingASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        eave_state = self.eave_state(scope=scope)
        eave.stdlib.logger.info(
            f"Request Start: {eave_state.request_id}: {eave_state.request_method} {eave_state.request_path}",
            extra=eave_state.log_context,
        )
        await self.app(scope, receive, send)
        eave.stdlib.logger.info(
            f"Request End: {eave_state.request_id}: {eave_state.request_method} {eave_state.request_path}",
            extra=eave_state.log_context,
        )
