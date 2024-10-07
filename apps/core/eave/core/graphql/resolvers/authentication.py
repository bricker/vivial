import eave.core.internal.database
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal.orm.account import AccountOrm


async def login(request: Request) -> Response:

    async with eave.core.internal.database.async_session.begin() as db_session:
        account = await AccountOrm.one_or_exception(
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