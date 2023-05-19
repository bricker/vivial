import eave.stdlib.core_api as eave_core
from starlette.requests import Request
from starlette.responses import Response

import eave.core.public.request_state as eave_request_util
from eave.core.internal import app_config
from eave.stdlib.logging import eaveLogger

from ...http_endpoint import HTTPEndpoint
from . import shared


class BaseOAuthCallback(HTTPEndpoint):
    request: Request
    response: Response
    state: str
    code: str
    auth_provider: eave_core.enums.AuthProvider
    eave_state: eave_request_util.EaveRequestState

    async def get(self, request: Request) -> Response:
        request = request
        response = Response()
        state = request.query_params["state"]
        shared.verify_oauth_state_or_exception(
            state=state, auth_provider=self.auth_provider, request=request, response=response
        )

        eave_state = eave_request_util.get_eave_state(request=request)

        code = request.query_params.get("code")
        error = request.query_params.get("error")
        error_description = request.query_params.get("error_description")

        if error or not code:
            eaveLogger.warning(
                f"Error response from {self.auth_provider} oauth flow, or code missing. {error}: {error_description}",
                extra=eave_state.log_context,
            )
            shared.set_redirect(response=response, location=app_config.eave_www_base)
            return response

        self.request = request
        self.response = response
        self.state = state
        self.code = code
        self.eave_state = eave_state

        return self.response
