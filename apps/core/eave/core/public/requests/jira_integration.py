from typing import Literal, cast

from asgiref.typing import HTTPScope
from starlette.types import Scope
import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
from eave.core.internal.orm.jira_installation import JiraInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.core.public.http_endpoint import HTTPEndpoint
from eave.stdlib.core_api.models.integrations import Integration
from eave.stdlib.core_api.operations.jira import RegisterJiraIntegrationRequest
from eave.stdlib.exceptions import BadRequestError


from eave.stdlib import analytics
from eave.stdlib.config import shared_config
import eave.stdlib.api_util as eave_api_util
from starlette.requests import Request
from starlette.responses import Response


# class QueryJiraIntegration(HTTPEndpoint):
#     async def post(self, request: Request) -> Response:
#         body = await request.json()
#         input = QueryJiraInstallation.RequestBody.parse_obj(body)

#         async with eave_db.async_session.begin() as db_session:
#             installation = await JiraInstallationOrm.one_or_exception(
#                 session=db_session,
#                 client_key=input.jira_integration.client_key,
#             )

#             if installation.team_id:
#                 eave_team = await eave_orm.TeamOrm.one_or_exception(
#                     session=db_session,
#                     team_id=installation.team_id,
#                 )
#             else:
#                 eave_team = None

#         return eave_api_util.json_response(
#             QueryJiraInstallation.ResponseBody(
#                 team=eave_team.api_model if eave_team else None,
#                 jira_integration=installation.api_model,
#             )
#         )


class RegisterJiraIntegrationEndpoint(HTTPEndpoint):
    """
    Creates or update a Jira integration.
    If the given client_key already exists, this endpoint updates the existing integration.
    If it doesn't exist, it creates a new integration.
    The client_key is unique and will never change.
    https://developer.atlassian.com/cloud/confluence/connect-app-descriptor/#lifecycle
    """

    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = RegisterJiraIntegrationRequest.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            integration = await JiraInstallationOrm.one_or_none(
                session=db_session, client_key=input.jira_integration.client_key,
            )

            if not integration:
                """
                If the baseUrl exists with a different client key, Atlassian suggests updating that record with the new
                client key as a workaround, but it also says that baseUrl isn't unique and shouldn't be used as an identifier. So
                I'll lean cautious here and ignore that case.
                https://developer.atlassian.com/cloud/confluence/connect-app-descriptor/#lifecycle-attribute-example
                https://ecosystem.atlassian.net/browse/AC-1528
                """
                integration = await JiraInstallationOrm.create(
                    session=db_session,
                    input=input.jira_integration,
                )

                team = None

                analytics.log_event(
                    event_name="eave_application_integration",
                    event_description="An integration was added for a team",
                    eave_team_id=None,
                    event_source="core api",
                    opaque_params={
                        "integration_name": Integration.jira.value,
                        "atlassian_site_url": input.jira_integration.base_url,
                        "atlassian_site_description": input.jira_integration.description,
                        "atlassian_actor_account_id": input.jira_integration.atlassian_actor_account_id,
                    },
                )

            else:
                integration.update(
                    session=db_session,
                    input=input.jira_integration,
                )

                if integration.team_id:
                    team = await TeamOrm.one_or_exception(session=db_session, team_id=integration.team_id)
                else:
                    team = None

                analytics.log_event(
                    event_name="eave_application_integration_updated",
                    event_description="An integration was updated for a team",
                    eave_team_id=integration.team_id,
                    event_source="core api",
                    opaque_params={
                        "integration_name": Integration.jira.value,
                        "atlassian_site_url": input.jira_integration.base_url,
                        "atlassian_site_description": input.jira_integration.description,
                        "atlassian_actor_account_id": input.jira_integration.atlassian_actor_account_id,
                        "fields_given": sorted(input.jira_integration.__fields_set__),
                    },
                )

        return eave_api_util.json_response(
            RegisterJiraIntegrationRequest.ResponseBody(
                team=team.api_model if team else None,
                jira_integration=integration.api_model,
            )
        )


# class UpdateForgeIntegration(HTTPEndpoint):
#     async def post(self, request: Request) -> Response:
#         body = await request.json()
#         input = UpdateJiraInstallation.RequestBody.parse_obj(body)

#         async with eave_db.async_session.begin() as db_session:
#             installation = await eave_orm.JiraInstallationOrm.one_or_exception(
#                 session=db_session,
#                 forge_app_installation_id=input.jira_integration.forge_app_installation_id,
#             )

#             previous_version = installation.forge_app_version

#             if installation.team_id:
#                 eave_team = await eave_orm.TeamOrm.one_or_exception(session=db_session, team_id=installation.team_id)
#             else:
#                 eave_team = None

#             installation.update(session=db_session, input=input.jira_integration)

#         analytics.log_event(
#             event_name="eave_forge_app_updated",
#             event_description="The team's forge app was updated",
#             eave_account_id="unknown",
#             eave_team_id=str(eave_team.id) if eave_team else None,
#             eave_visitor_id="unknown",
#             event_source="core api",
#             opaque_params={
#                 "integration_name": Integration.forge.value,
#                 "installer_atlassian_account_id": input.jira_integration.forge_app_installer_account_id,
#                 "forge_app_installation_id": input.jira_integration.forge_app_installation_id,
#                 "forge_app_previous_version": previous_version,
#                 "forge_app_new_version": input.jira_integration.forge_app_version,
#             },
#         )

#         return eave_api_util.json_response(
#             UpdateJiraInstallation.ResponseBody(
#                 team=eave_team.api_model if eave_team else None,
#                 jira_integration=installation.api_model,
#             )
#         )
