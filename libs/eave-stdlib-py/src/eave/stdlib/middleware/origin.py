import asgiref.typing
import starlette.types

from eave.stdlib.core_api.operations import EndpointConfiguration

from .base import EaveASGIMiddleware
from ..api_util import get_header_value
from ..headers import EAVE_ORIGIN_HEADER
from ..exceptions import InvalidOriginError, MissingRequiredHeaderError
from ..eave_origins import EaveApp
from ..request_state import EaveRequestState


class OriginASGIMiddleware(EaveASGIMiddleware):
    endpoint_config: EndpointConfiguration

    def __init__(self, app: starlette.types.ASGIApp, endpoint_config: EndpointConfiguration) -> None:
        super().__init__(app)
        self.endpoint_config = endpoint_config

    async def run(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        if scope["type"] == "http":
            self._process_origin(scope=scope)

        await self.app(scope, receive, send)

    def _process_origin(self, scope: asgiref.typing.HTTPScope) -> None:
        eave_state = EaveRequestState.load(scope=scope)
        origin_header = get_header_value(scope=scope, name=EAVE_ORIGIN_HEADER)
        if not origin_header:
            if not self.endpoint_config.origin_required:
                return
            else:
                raise MissingRequiredHeaderError(EAVE_ORIGIN_HEADER)

        try:
            origin = EaveApp(value=origin_header)
            eave_state.ctx.eave_origin = str(origin)
        except ValueError:
            raise InvalidOriginError()
