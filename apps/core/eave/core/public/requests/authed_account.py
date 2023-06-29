import eave.stdlib.api_util
import eave.stdlib.util
import eave.core.internal
import eave.core.public
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.core_api.operations.account import (
    GetAuthenticatedAccount,
    GetAuthenticatedAccountTeamIntegrations,
)
from eave.stdlib.request_state import EaveRequestState


class GetAuthedAccount(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team_orm = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
            )
            eave_account_orm = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session, id=eave.stdlib.util.unwrap(eave_state.ctx.eave_account_id)
            )

        return eave.stdlib.api_util.json_response(
            GetAuthenticatedAccount.ResponseBody(
                account=eave_account_orm.api_model,
                team=eave_team_orm.api_model,
            )
        )


class GetAuthedAccountTeamIntegrations(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team_orm = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
            )
            eave_account_orm = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session, id=eave.stdlib.util.unwrap(eave_state.ctx.eave_account_id)
            )
            integrations = await eave_team_orm.get_integrations(session=db_session)
            destination = await eave_team_orm.get_destination(session=db_session)

        return eave.stdlib.api_util.json_response(
            GetAuthenticatedAccountTeamIntegrations.ResponseBody(
                account=eave_account_orm.api_model,
                team=eave_team_orm.api_model,
                integrations=integrations,
                destination=destination,
            )
        )
