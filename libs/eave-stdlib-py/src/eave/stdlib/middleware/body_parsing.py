import json

from asgiref.typing import ASGIReceiveCallable, ASGIReceiveEvent, ASGISendCallable, Scope

from ..headers import CONTENT_TYPE

from .base import EaveASGIMiddleware
from ..api_util import get_header_value
from ..logging import eaveLogger

class BodyParsingASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body = await self.read_body(scope=scope, receive=receive)

        if len(body) > 0:
            with self.auto_eave_state(scope=scope) as eave_state:
                content_type = get_header_value(
                    scope=scope,
                    name=CONTENT_TYPE,
                )

                if content_type == "application/json":
                    try:
                        eave_state.parsed_request_body = json.loads(body)
                    except Exception:
                        eaveLogger.exception(
                            "Error while parsing body as JSON", extra=eave_state.log_context
                        )
                else:
                    eave_state.parsed_request_body = {"text": str(body)}

        async def dummy_receive() -> ASGIReceiveEvent:
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        await self.app(scope, dummy_receive, send)
