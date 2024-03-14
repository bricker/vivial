from typing import cast
import time
import hmac
import json
from uuid import UUID
from eave.stdlib import analytics, utm_cookies
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.core_api.models.account import AuthProvider

import google.oauth2.credentials
import google.oauth2.id_token
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

import eave.core.internal.oauth.google
from eave.core.internal.oauth import state_cookies as oauth_cookies
from eave.stdlib.exceptions import MissingOAuthCredentialsError
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.jwt import TEMP_create_jwt_for_metabase, JWTPurpose
from . import base, shared

class TEMP_MetabaseOAuthCallback(base.BaseOAuthCallback):
    async def get(self, request: Request) -> Response:
        await super().get(request=request)
        ctx = LogContext.wrap(scope=request.scope)

        account = await shared.get_or_create_eave_account(
            request=self.request,
            response=self.response,
            eave_team_name="Metabase Test Team",
            user_email="admin@eave.fyi",
            auth_provider=AuthProvider.google,
            auth_id=str(UUID()),
            access_token="12345",
            refresh_token="12345",
        )

        # do metabase stuff

        jwt = TEMP_create_jwt_for_metabase(
            email=account.email or "",
            first_name="Admin",
            last_name="Eave",
            exp_minutes=10,
            signing_key="8c1c4cb0017162745f294d4d67a8e249205f1057284809f13c8064f87c796fbf", # TODO make secrt
            purpose=JWTPurpose.access,
        )

        return_to = f"{SHARED_CONFIG.eave_public_www_base}/dashboard"
        shared.set_redirect(
            response=self.response,
            location=f"http://localhost:3000/auth/sso?jwt={jwt.signature}&return_to={return_to}"
        )
        return self.response
