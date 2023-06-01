from typing import Literal, cast

from asgiref.typing import HTTPScope
from starlette.types import Scope
import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
from eave.core.public.http_endpoint import HTTPEndpoint
from eave.stdlib.core_api.operations.forge import (
    RegisterForgeInstallation,
    UpdateForgeInstallation,
)
from eave.stdlib.core_api.models.integrations import Integration
from eave.stdlib.core_api.operations.forge import QueryForgeInstallation
from eave.stdlib.exceptions import BadRequestError


from eave.stdlib import analytics
from eave.stdlib.config import shared_config
import eave.stdlib.api_util as eave_api_util
from starlette.requests import Request
from starlette.responses import Response


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
        validate_shared_secret(scope=request.scope)  # FIXME: This should use real signing

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
                "integration_name": Integration.forge.value,
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

            previous_version = installation.forge_app_version

            if installation.team_id:
                eave_team = await eave_orm.TeamOrm.one_or_exception(session=db_session, team_id=installation.team_id)
            else:
                eave_team = None

            installation.update(session=db_session, input=input.forge_integration)

        analytics.log_event(
            event_name="eave_forge_app_updated",
            event_description="The team's forge app was updated",
            eave_account_id="unknown",
            eave_team_id=str(eave_team.id) if eave_team else None,
            eave_visitor_id="unknown",
            event_source="core api",
            opaque_params={
                "integration_name": Integration.forge.value,
                "installer_atlassian_account_id": input.forge_integration.forge_app_installer_account_id,
                "forge_app_installation_id": input.forge_integration.forge_app_installation_id,
                "forge_app_previous_version": previous_version,
                "forge_app_new_version": input.forge_integration.forge_app_version,
            },
        )

        return eave_api_util.json_response(
            UpdateForgeInstallation.ResponseBody(
                team=eave_team.api_model if eave_team else None,
                forge_integration=installation.api_model,
            )
        )


def validate_shared_secret(scope: Scope) -> Literal[True]:
    cscope = cast(HTTPScope, scope)
    given_secret = eave_api_util.get_bearer_token(scope=cscope)
    if given_secret is None:
        raise BadRequestError("malformed or missing authorization header")

    shared_secret = shared_config.eave_forge_app_shared_secret

    if given_secret != shared_secret:
        raise BadRequestError("malformed or missing authorization header")

    return True
