from typing import cast

from asgiref.typing import HTTPScope
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.team import TeamOrm
import eave.stdlib.api_util
import eave.stdlib.util
import eave.core.internal
import eave.core.public
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.core_api.operations.account import (
    GetAuthenticatedAccount,
)
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.http_endpoint import HTTPEndpoint


class GetAuthedAccount(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
            )
            eave_account_orm = await AccountOrm.one_or_exception(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=eave.stdlib.util.ensure_uuid(eave_state.ctx.eave_account_id),
                    access_token=eave.stdlib.api_util.get_bearer_token(scope=cast(HTTPScope, request.scope)),
                ),
            )

        return eave.stdlib.api_util.json_response(
            GetAuthenticatedAccount.ResponseBody(
                account=eave_account_orm.api_model,
                team=eave_team_orm.api_model,
            )
        )
