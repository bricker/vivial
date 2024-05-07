import time
from urllib.parse import quote, unquote, urlencode, urlparse, urlunparse

import aiohttp
from aiohttp.hdrs import METH_GET
from asgiref.typing import HTTPScope
from eave.stdlib.api_util import set_redirect
from eave.stdlib.exceptions import NotFoundError, UnauthorizedError
from eave.stdlib.logging import LOGGER
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

from eave.core.internal.orm.metabase_instance import MetabaseInstanceOrm

class MetabaseAuthProxyEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, state: EaveRequestState) -> Response:
        """
        Redirects request to the authenticated user's metabase instance to set SSO
        cookies before redirecting in turn to the metabase dashboard specified in the
        `return_to` query parameter.
        This endpoint resolves to a redirect to an HTML page on success and is intended
        to be the src for an iframe element.
        """
        async with database.async_session.begin() as db_session:
            account = await AccountOrm.one_or_exception(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=ensure_uuid(state.ctx.eave_account_id),
                ),
            )

            metabase_instance = await MetabaseInstanceOrm.one_or_exception(
                session=db_session,
                team_id=account.team_id,
            )

        if not metabase_instance.jwt_signing_key or not metabase_instance.jwt_signing_key:
            raise NotFoundError("Metabase instance can't be reached.")

        email = account.email or "unknown"

        full_jwt = jwt.encode(
            payload={
                "email": email,
                "first_name": email.split("@")[0] or "unknown",
                "exp": round(time.time()) + (60 * 10),  # 10min
            },
            key=metabase_instance.jwt_signing_key,
        )

        return_to_str = self._build_qp()

        async with aiohttp.ClientSession() as session:
            # Get the response from Metabase
            response = await session.request(
                method=METH_GET, # Only GET supported currently
                url=f"{metabase_instance.internal_base_url}/auth/sso",
                params={
                    "jwt": full_jwt,
                    "return_to": return_to_str,
                },
                headers=request.headers,
                cookies=request.cookies,
                allow_redirects=True,
            )

            # Consume the body while the session is still open
            body = await response.read()

        LOGGER.info("metabase response", state.ctx, { "body": str(body), "headers": dict(response.headers), "status": response.status })

        response = Response(
            status_code=response.status,
            content=body,
            media_type=response.content_type,
        )

        return response

    def _build_qp(self) -> str:
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
        return_to_str = self.request.query_params.get("return_to") or "/dashboard/1"
        return_to_str = unquote(return_to_str)  # In case return_to qp has its own query params
        return_to_url = urlparse(return_to_str)
        sep = "&" if return_to_url.query else ""
        return_to_url = return_to_url._replace(query=f"{return_to_url.query}{sep}{qp}")

        # Now reverse the decoding done above
        return_to_str = urlunparse(return_to_url)
        return_to_str = quote(return_to_str)
        return return_to_str
