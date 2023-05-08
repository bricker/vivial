from starlette.responses import Response
from starlette.requests import Request

import eave.core.internal.database as db
import eave.core.internal.orm as orm
import eave.core.public.request_state as rutil
import eave.stdlib.api_util as autil
import eave.stdlib.core_api.models as models
import eave.stdlib.core_api.operations as ops
from ..http_endpoint import HTTPEndpoint


class GetAuthedAccount(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = rutil.get_eave_state(request=request)
        eave_account_orm = eave_state.eave_account
        eave_team_orm = eave_state.eave_team

        eave_team = models.Team.from_orm(eave_team_orm)
        eave_account = models.AuthenticatedAccount.from_orm(eave_account_orm)

        return autil.json_response(ops.GetAuthenticatedAccount.ResponseBody(
            account=eave_account,
            team=eave_team,
        ))

class GetAuthedAccountTeamIntegrations(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = rutil.get_eave_state(request=request)
        eave_account_orm = eave_state.eave_account
        eave_team_orm = eave_state.eave_team

        async with db.async_session.begin() as db_session:
            integrations = await eave_team_orm.get_integrations(session=db_session)

        eave_team = models.Team.from_orm(eave_team_orm)
        eave_account = models.AuthenticatedAccount.from_orm(eave_account_orm)

        return autil.json_response(ops.GetAuthenticatedAccountTeamIntegrations.ResponseBody(
            account=eave_account,
            team=eave_team,
            integrations=integrations,
        ))

class UpdateAtlassianIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = rutil.get_eave_state(request=request)
        body = await request.json()
        input = ops.UpdateAtlassianInstallation.RequestBody.parse_obj(body)

        eave_account_orm = eave_state.eave_account
        eave_team_orm = eave_state.eave_team

        async with db.async_session.begin() as db_session:
            installation = await orm.AtlassianInstallationOrm.one_or_exception(
                session=db_session,
                team_id=eave_team_orm.id,
            )

            if input.atlassian_integration.confluence_space_key is not None:
                installation.confluence_space_key = input.atlassian_integration.confluence_space_key

        eave_team = models.Team.from_orm(eave_team_orm)
        eave_account = models.AuthenticatedAccount.from_orm(eave_account_orm)
        atlassian_integration = models.AtlassianInstallation.from_orm(installation)

        return autil.json_response(ops.UpdateAtlassianInstallation.ResponseBody(
            account=eave_account,
            team=eave_team,
            atlassian_integration=atlassian_integration,
        ))
