from typing import Optional
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.core_api.models.account import AuthProvider

from eave.stdlib.logging import eaveLogger
from eave.stdlib.request_state import EaveRequestState

from eave.stdlib.http_endpoint import HTTPEndpoint
from . import shared


class BaseOAuthCallback(HTTPEndpoint):
    request: Request
    response: Response
    state: str
    code: Optional[str]
    error: Optional[str]
    error_description: Optional[str]
    auth_provider: AuthProvider
    eave_state: EaveRequestState

    async def get(self, request: Request) -> Response:
        request = request
        response = Response()
        state = request.query_params["state"]
        shared.verify_oauth_state_or_exception(
            state=state, auth_provider=self.auth_provider, request=request, response=response
        )

        eave_state = EaveRequestState.load(request=request)

        self.code = request.query_params.get("code")
        self.error = request.query_params.get("error")
        self.error_description = request.query_params.get("error_description")

        self.request = request
        self.response = response
        self.state = state
        self.eave_state = eave_state

        return self.response

    def _check_valid_callback(self) -> bool:
        if self.error or not self.code:
            eaveLogger.warning(
                f"Error response from {self.auth_provider} oauth flow, or code missing. {self.error}: {self.error_description}",
                self.eave_state.ctx,
            )
            shared.cancel_flow(response=self.response)
            return False

        return True
