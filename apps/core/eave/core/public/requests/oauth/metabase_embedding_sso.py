import jwt
import time
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from eave.core.internal import database
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.orm.account import AccountOrm
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import ensure_uuid
from . import shared


class MetabaseEmbeddingSSO(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        """
        Redirects request to the authenticated user's metabase instance to set SSO
        cookies before redirecting in turn to the metabase dashboard specified in the
        `return_to` query parameter.
        This endpoint resolves to an HTML page on success and is intended to be the src
        for an iframe element.
        """
        eave_state = EaveRequestState.load(request=request)

        # this must be a relative path to a metabase dashboard
        # https://www.metabase.com/docs/v0.48/embedding/interactive-embedding-quick-start-guide#embed-metabase-in-your-app
        # TODO: if empty default to user's first dash we created
        return_to = request.query_params.get("return_to") or "/dashboard/8"
        response = Response()

        async with database.async_session.begin() as db_session:
            account = await AccountOrm.one_or_exception(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=ensure_uuid(eave_state.ctx.eave_account_id)
                ),
            )

        full_jwt = jwt.encode(
            {
                "email": account.email,
                "exp": round(time.time()) + (60 * 10),  # 10min
            },
            CORE_API_APP_CONFIG.metabase_jwt_key,  # TODO: pull correct value for this from user team db entry (and delete this config val)
        )

        # TODO: route to proper metabase instance for user's team
        shared.set_redirect(
            response=response,
            location=f"{SHARED_CONFIG.eave_public_metabase_base}/auth/sso?jwt={full_jwt}&return_to={return_to}",
        )
        return response
