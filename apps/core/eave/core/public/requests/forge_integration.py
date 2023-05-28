import eave.core.internal.database as eave_db
from eave.core.internal import app_config
import eave.core.internal.orm as eave_orm
from eave.core.internal.orm.team import TeamOrm
from eave.core.public.http_endpoint import HTTPEndpoint
from eave.stdlib.core_api.operations.forge import QueryForgeInstallation, RegisterForgeInstallation, UpdateForgeInstallation


import eave.stdlib.util
from eave.stdlib import analytics
import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api as eave_core
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.exceptions import NotFoundError
from eave.stdlib.request_state import get_eave_state


class QueryForgeIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = QueryForgeInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.ForgeInstallationOrm.one_or_exception(
                session=db_session,
                forge_app_installation_id=input.forge_integration.forge_app_installation_id,
            )

            if installation.team_id:
                eave_team = await eave_orm.TeamOrm.one_or_exception(
                    session=db_session,
                    team_id=installation.team_id,
                )
            else:
                eave_team = None

        return eave_api_util.json_response(
            QueryForgeInstallation.ResponseBody(
                team=eave_team.api_model if eave_team else None,
                forge_integration=installation.api_model,
            )
        )


class RegisterForgeIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = RegisterForgeInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation_orm = await eave_orm.ForgeInstallationOrm.create(
                session=db_session,
                input=input.forge_integration,
            )

        analytics.log_event(
            event_name="eave_application_integration",
            event_description="An integration was added for a team",
            eave_account_id="unknown",
            eave_team_id="unknown",
            eave_visitor_id="unknown",
            event_source="core api forge registration",
            opaque_params={
                "integration_name": eave.stdlib.core_api.enums.Integration.forge.value,
                "installer_atlassian_account_id": input.forge_integration.forge_app_installer_account_id,
                "forge_app_installation_id": input.forge_integration.forge_app_installation_id,
                "forge_app_version": input.forge_integration.forge_app_version,
            },
        )
        return eave_api_util.json_response(
            RegisterForgeInstallation.ResponseBody(
                forge_integration=installation_orm.api_model,
            )
        )

class UpdateForgeIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = UpdateForgeInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.ForgeInstallationOrm.one_or_exception(
                session=db_session,
                forge_app_installation_id=input.forge_integration.forge_app_installation_id,
            )

            if installation.team_id:
                eave_team = await eave_orm.TeamOrm.one_or_exception(session=db_session, team_id=installation.team_id)
            else:
                eave_team = None

            installation.update(
                session=db_session,
                input=input.forge_integration
            )

        return eave_api_util.json_response(
            UpdateForgeInstallation.ResponseBody(
                team=eave_team.api_model if eave_team else None,
                forge_integration=installation.api_model,
            )
        )