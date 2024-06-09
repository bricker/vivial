from typing import cast

import google.oauth2.credentials
import google.oauth2.id_token
from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

import eave.core.internal.oauth.google
from eave.core.internal.oauth import state_cookies as oauth_cookies
from eave.stdlib import utm_cookies
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.exceptions import MissingOAuthCredentialsError
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext

from . import base, shared

_AUTH_PROVIDER = AuthProvider.google


class GoogleOAuthAuthorize(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        oauth_flow_info = eave.core.internal.oauth.google.get_oauth_flow_info()
        response = RedirectResponse(url=oauth_flow_info.authorization_url)

        utm_cookies.set_tracking_cookies(
            response=response,
            request=request,
        )

        oauth_cookies.save_state_cookie(
            response=response,
            state=oauth_flow_info.state,
            provider=_AUTH_PROVIDER,
        )

        return response


class GoogleOAuthCallback(base.BaseOAuthCallback):
    auth_provider = _AUTH_PROVIDER

    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        await super().handle(request=request, scope=scope, ctx=ctx)

        if not self._check_valid_callback():
            return self.response

        flow = eave.core.internal.oauth.google.build_flow(state=self.oauth_state)
        flow.fetch_token(code=self.code)

        # flow.credentials returns a `google.auth.credentials.Credentials`, which is the base class of
        # google.oauth2.credentials.Credentials and doesn't contain common oauth properties like refresh_token.
        # The `cast` here gives us type hints, autocomplete, etc. for `flow.credentials`
        credentials = cast(google.oauth2.credentials.Credentials, flow.credentials)
        if credentials.id_token is None:
            raise MissingOAuthCredentialsError("google oauth2 credentials")

        google_token = eave.core.internal.oauth.google.decode_id_token(id_token=credentials.id_token)
        eave_team_name = f"{google_token.given_name}'s Team" if google_token.given_name else shared.DEFAULT_TEAM_NAME

        await shared.get_or_create_eave_account(
            request=request,
            response=self.response,
            eave_team_name=eave_team_name,
            user_email=google_token.email,
            auth_provider=self.auth_provider,
            auth_id=google_token.sub,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            ctx=ctx,
        )

        return self.response
