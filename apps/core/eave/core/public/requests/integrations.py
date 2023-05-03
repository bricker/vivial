import eave.core.internal.database
import eave.core.internal.orm.account
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.github_installation
import eave.core.internal.orm.slack_installation
import eave.core.internal.orm.team
import eave.core.public.requests.util
import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models
import eave.stdlib.core_api.operations
import fastapi


async def slack(
    input: eave.stdlib.core_api.operations.GetSlackInstallation.RequestBody,
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.GetSlackInstallation.ResponseBody:
    async with eave.core.internal.database.async_session.begin() as db_session:
        installation = await eave.core.internal.orm.slack_installation.SlackInstallationOrm.one_or_exception(
            session=db_session,
            slack_team_id=input.slack_integration.slack_team_id,
        )

        eave_team_orm = await eave.core.internal.orm.team.TeamOrm.one_or_exception(
            session=db_session,
            team_id=installation.team_id,
        )

    eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
    integration = eave.stdlib.core_api.models.SlackInstallation.from_orm(installation)

    return eave.stdlib.core_api.operations.GetSlackInstallation.ResponseBody(
        slack_integration=integration,
        team=eave_team,
    )


async def github(
    input: eave.stdlib.core_api.operations.GetGithubInstallation.RequestBody,
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.GetGithubInstallation.ResponseBody:
    async with eave.core.internal.database.async_session.begin() as db_session:
        installation = await eave.core.internal.orm.github_installation.GithubInstallationOrm.one_or_exception(
            session=db_session,
            github_install_id=input.github_integration.github_install_id,
        )

        eave_team = await eave.core.internal.orm.team.TeamOrm.one_or_exception(
            session=db_session,
            team_id=installation.team_id,
        )

    return eave.stdlib.core_api.operations.GetGithubInstallation.ResponseBody(
        github_integration=eave.stdlib.core_api.models.GithubInstallation.from_orm(installation),
        team=eave.stdlib.core_api.models.Team.from_orm(eave_team),
    )


async def atlassian(
    input: eave.stdlib.core_api.operations.GetAtlassianInstallation.RequestBody,
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.GetAtlassianInstallation.ResponseBody:
    async with eave.core.internal.database.async_session.begin() as db_session:
        installation = await eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm.one_or_exception(
            session=db_session,
            atlassian_cloud_id=input.atlassian_integration.atlassian_cloud_id,
        )

        eave_team = await eave.core.internal.orm.team.TeamOrm.one_or_exception(
            session=db_session,
            team_id=installation.team_id,
        )

    return eave.stdlib.core_api.operations.GetAtlassianInstallation.ResponseBody(
        atlassian_integration=eave.stdlib.core_api.models.AtlassianInstallation.from_orm(installation),
        team=eave.stdlib.core_api.models.Team.from_orm(eave_team),
    )
