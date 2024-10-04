from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal
import eave.core.public
from eave.core.internal.orm.account import AccountOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.account import (
    GetMyAccountRequest,
)
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class GetMyAccountEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_account_orm = await AccountOrm.one_or_exception(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=ensure_uuid(ctx.eave_authed_account_id),
                ),
            )

        return json_response(
            GetMyAccountRequest.ResponseBody(
                account=eave_account_orm.api_model,
            )
        )
