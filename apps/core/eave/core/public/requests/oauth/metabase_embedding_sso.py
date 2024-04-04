import time

import jwt
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal import database
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.metabase_instance import MetabaseInstanceOrm
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import ensure_uuid
from urllib.parse import urlencode, quote

from . import shared


class MetabaseEmbeddingSSO(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        """
        Redirects request to the authenticated user's metabase instance to set SSO
        cookies before redirecting in turn to the metabase dashboard specified in the
        `return_to` query parameter.
        This endpoint resolves to a redirect to an HTML page on success and is intended
        to be the src for an iframe element.
        """
        eave_state = EaveRequestState.load(request=request)

        # this must be a relative path to a metabase dashboard
        # https://www.metabase.com/docs/v0.48/embedding/interactive-embedding-quick-start-guide#embed-metabase-in-your-app
        # TODO: if empty default to user's first dash we created
        qp = urlencode({
            "top_nav": "true",
            "new_button": "true",
            "logo": "false",
            "side_nav": "false",
            "breadcrumbs": "false",
            "search": "false",
            "header": "true",
            "action_buttons": "true",
        })
        return_to = request.query_params.get("return_to") or quote(f"/dashboard/8?{qp}")
        response = Response()

        async with database.async_session.begin() as db_session:
            account = await AccountOrm.one_or_exception(
                session=db_session,
                params=AccountOrm.QueryParams(id=ensure_uuid(eave_state.ctx.eave_account_id)),
            )

            metabase_instance = await MetabaseInstanceOrm.one_or_exception(
                session=db_session,
                team_id=account.team_id,
            )
            # validate instance hosting setup is complete before redirecting to instance
            metabase_instance.validate_hosting_data()

        full_jwt = jwt.encode(
            {
                "email": account.email,
                "exp": round(time.time()) + (60 * 10),  # 10min
            },
            metabase_instance.jwt_signing_key,  # type: ignore
        )

        # route to proper metabase instance for user's team
        shared.set_redirect(
            response=response,
            location="/".join(
                [
                    SHARED_CONFIG.eave_public_metabase_base,
                    # metabase_instance.route_id, # TODO: uncomment once mb instance deployment to subpaths is setup
                    "auth",
                    f"sso?jwt={full_jwt}&return_to={return_to}",
                ]
            ),
        )
        return response
