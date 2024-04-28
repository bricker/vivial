import time
from urllib.parse import quote, unquote, urlencode, urlparse, urlunparse

import jwt
from starlette.requests import Request
from starlette.responses import Response

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
        This endpoint resolves to a redirect to an HTML page on success and is intended
        to be the src for an iframe element.
        """
        eave_state = EaveRequestState.load(request=request)

        # modify metabase UI using query params
        # https://www.metabase.com/docs/latest/embedding/interactive-embedding#showing-or-hiding-metabase-ui-components
        qp = urlencode(
            {
                "top_nav": "true",
                "new_button": "true",
                "logo": "false",
                "side_nav": "false",
                "breadcrumbs": "false",
                "search": "false",
                "header": "true",
                "action_buttons": "true",
            }
        )
        # this must be a relative path to a metabase dashboard
        # https://www.metabase.com/docs/v0.48/embedding/interactive-embedding-quick-start-guide#embed-metabase-in-your-app
        # TODO: if empty default to user's first dash we created
        return_to_str = request.query_params.get("return_to") or "/dashboard/1"
        return_to_str = unquote(return_to_str)  # In case return_to qp has its own query params
        return_to_url = urlparse(return_to_str)
        sep = "&" if return_to_url.query else ""
        return_to_url = return_to_url._replace(query=f"{return_to_url.query}{sep}{qp}")
        # Now reverse the decoding done above
        return_to_str = urlunparse(return_to_url)
        return_to_str = quote(return_to_str)

        response = Response()

        async with database.async_session.begin() as db_session:
            account = await AccountOrm.one_or_exception(
                session=db_session,
                params=AccountOrm.QueryParams(id=ensure_uuid(eave_state.ctx.eave_account_id)),
            )

            # metabase_instance = await MetabaseInstanceOrm.one_or_exception(
            #     session=db_session,
            #     team_id=account.team_id,
            # )
            # # validate instance hosting setup is complete before redirecting to instance
            # metabase_instance.validate_hosting_data()

        full_jwt = jwt.encode(
            {
                "email": account.email,
                "exp": round(time.time()) + (60 * 10),  # 10min
            },
            CORE_API_APP_CONFIG.metabase_jwt_key,
        )

        # route to proper metabase instance for user's team
        shared.set_redirect(
            response=response,
            location="/".join(
                [
                    SHARED_CONFIG.eave_public_metabase_base,
                    "auth",
                    f"sso?jwt={full_jwt}&return_to={return_to_str}",
                ]
            ),
        )
        return response
