import uuid
import jwt
from eave.stdlib.core_api.models.account import AuthProvider

from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from eave.stdlib.http_endpoint import HTTPEndpoint
from . import shared


class TEMP_MetabaseOAuthCallback(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        # await super().get(request=request)
        response = RedirectResponse("/")

        account = await shared.get_or_create_eave_account(
            request=request,
            response=response,
            eave_team_name="Metabase Test Team",
            user_email="admin@eave.fyi",
            auth_provider=AuthProvider.google,
            auth_id=str(uuid.uuid4()),
            access_token="12345",
            refresh_token="12345",
        )

        # do metabase stuff
        import time

        full_jwt = jwt.encode(
            {
                "email": account.email or "dummy@email.com",
                "first_name": "Admin",
                "last_name": "Eave",
                "exp": round(time.time()) + (60 * 10),  # 10min
            },
            "527d96216242062a3d2355c97690ddc584d79217d2f7abbbfcf2afa240ab556d",  # TODO make secrt
        )

        # this must be a relative path to a metabase dashboard
        # https://www.metabase.com/docs/v0.48/embedding/interactive-embedding-quick-start-guide#embed-metabase-in-your-app
        return_to = "/dashboard/1"
        shared.set_redirect(
            response=response, location=f"http://localhost:3000/auth/sso?jwt={full_jwt}&return_to={return_to}"
        )
        return response
