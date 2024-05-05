from typing import cast, override

from asgiref.typing import HTTPScope
from eave.stdlib.api_util import get_bearer_token, get_header_value_or_exception, json_response
from eave.stdlib.headers import EAVE_ACCOUNT_ID_HEADER
from eave.stdlib.util import ensure_uuid
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal
import eave.core.public
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.core_api.operations.account import (
    GetMyAccountRequest,
)
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.request_state import EaveRequestState


class GetAccountEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, state: EaveRequestState) -> Response:
        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_account_orm = await AccountOrm.one_or_exception(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=ensure_uuid(state.ctx.eave_account_id),
                ),
            )
            eave_team_orm = await TeamOrm.one_or_exception(
                session=db_session, team_id=eave_account_orm.team_id,
            )

        return json_response(
            GetMyAccountRequest.ResponseBody(
                account=eave_account_orm.api_model,
                team=eave_team_orm.api_model,
            )
        )
