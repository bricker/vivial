import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api as eave_core
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.request_state as eave_rutil
from eave.stdlib.exceptions import NotFoundError


from ..http_endpoint import HTTPEndpoint


class SlackIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        """
        Raises an exception if no SlackInstallation can be found, or if there is
        a problem refreshing the SlackInstallation access tokens.
        """
        eave_rutil.get_eave_state(request=request)
        body = await request.json()
        input = eave_core.operations.GetSlackInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.SlackInstallationOrm.one_or_none(
                session=db_session,
                slack_team_id=input.slack_integration.slack_team_id,
            )

            if not installation:
                raise NotFoundError()

            # ensure access tokens are up to date
            await installation.refresh_token_or_exception(session=db_session)

            eave_team_orm = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        eave_team = eave_core.models.Team.from_orm(eave_team_orm)
        integration = eave_core.models.SlackInstallation.from_orm(installation)

        model = eave_core.operations.GetSlackInstallation.ResponseBody(
            slack_integration=integration,
            team=eave_team,
        )

        return eave_api_util.json_response(model=model)


class GithubIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_rutil.get_eave_state(request=request)
        body = await request.json()
        input = eave_core.operations.GetGithubInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.GithubInstallationOrm.one_or_none(
                session=db_session,
                github_install_id=input.github_integration.github_install_id,
            )

            if not installation:
                raise NotFoundError()

            eave_team = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        eave_team = eave_core.models.Team.from_orm(eave_team)
        integration = eave_core.models.GithubInstallation.from_orm(installation)

        return eave_api_util.json_response(
            eave_core.operations.GetGithubInstallation.ResponseBody(
                github_integration=integration,
                team=eave_team,
            )
        )


class AtlassianIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_rutil.get_eave_state(request=request)
        body = await request.json()
        input = eave_core.operations.GetAtlassianInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.AtlassianInstallationOrm.one_or_none(
                session=db_session,
                atlassian_cloud_id=input.atlassian_integration.atlassian_cloud_id,
            )

            if not installation:
                raise NotFoundError()

            eave_team = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        eave_team = eave_core.models.Team.from_orm(eave_team)
        integration = eave_core.models.AtlassianInstallation.from_orm(installation)

        return eave_api_util.json_response(
            eave_core.operations.GetAtlassianInstallation.ResponseBody(
                atlassian_integration=integration,
                team=eave_team,
            )
        )
