import eave.stdlib
import eave.core.internal
import eave.core.public
from starlette.requests import Request
from starlette.responses import Response
import eave.stdlib.lib.request_state as request_state

class GetAuthedAccount(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = request_state.get_eave_state(request=request)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team_orm = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )
            eave_account_orm = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session, id=eave.stdlib.util.unwrap(eave_state.eave_account_id)
            )

        eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
        eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_account_orm)

        return eave.stdlib.api_util.json_response(
            eave.stdlib.core_api.operations.GetAuthenticatedAccount.ResponseBody(
                account=eave_account,
                team=eave_team,
            )
        )


class GetAuthedAccountTeamIntegrations(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = request_state.get_eave_state(request=request)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team_orm = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )
            eave_account_orm = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session, id=eave.stdlib.util.unwrap(eave_state.eave_account_id)
            )
            integrations = await eave_team_orm.get_integrations(session=db_session)

        eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
        eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_account_orm)

        return eave.stdlib.api_util.json_response(
            eave.stdlib.core_api.operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(
                account=eave_account,
                team=eave_team,
                integrations=integrations,
            )
        )


class UpdateAtlassianIntegration(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = request_state.get_eave_state(request=request)
        body = await request.json()
        input = eave.stdlib.core_api.operations.UpdateAtlassianInstallation.RequestBody.parse_obj(body)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team_orm = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )
            eave_account_orm = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session, id=eave.stdlib.util.unwrap(eave_state.eave_account_id)
            )

            installation = await eave.core.internal.orm.AtlassianInstallationOrm.one_or_exception(
                session=db_session,
                team_id=eave_team_orm.id,
            )

            if input.atlassian_integration.confluence_space_key is not None:
                installation.confluence_space_key = input.atlassian_integration.confluence_space_key

        eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
        eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_account_orm)
        atlassian_integration = eave.stdlib.core_api.models.AtlassianInstallation.from_orm(installation)

        return eave.stdlib.api_util.json_response(
            eave.stdlib.core_api.operations.UpdateAtlassianInstallation.ResponseBody(
                account=eave_account,
                team=eave_team,
                atlassian_integration=atlassian_integration,
            )
        )
