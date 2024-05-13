from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext, eaveLogger

from . import shared


class BaseOAuthCallback(HTTPEndpoint):
    response: Response
    oauth_state: str
    code: str | None
    error: str | None
    error_description: str | None
    auth_provider: AuthProvider

    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        response = Response()
        oauth_state = request.query_params["state"]
        shared.verify_oauth_state_or_exception(
            state=oauth_state, auth_provider=self.auth_provider, request=request, response=response
        )

        self.code = request.query_params.get("code")
        self.error = request.query_params.get("error")
        self.error_description = request.query_params.get("error_description")

        self.response = response
        self.oauth_state = oauth_state

        return self.response

    def _check_valid_callback(self) -> bool:
        if self.error or not self.code:
            eaveLogger.warning(
                f"Error response from {self.auth_provider} oauth flow, or code missing. {self.error}: {self.error_description}",
                self.ctx,
            )
            shared.cancel_flow(response=self.response)
            return False

        return True
