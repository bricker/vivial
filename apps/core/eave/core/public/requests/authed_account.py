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
from eave.stdlib import logger


async def get_authed_account(
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.GetAuthenticatedAccount.ResponseBody:
    eave_state = eave.core.public.requests.util.get_eave_state(request=request)
    logger.info("authed_account.get_authed_account", extra=eave_state.log_context)

    eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_state.eave_team)
    eave_team.integrations = []

    async with eave.core.internal.database.async_session.begin() as db_session:
        slack_installation = await eave.core.internal.orm.slack_installation.SlackInstallationOrm.one_or_none(
            session=db_session, team_id=eave_team.id
        )
        if slack_installation:
            eave_team.integrations.append(eave.stdlib.core_api.enums.Integration.slack)

        # github_installation = await eave.core.internal.orm.slack_installation.GithubInstallationOrm.one_or_none(
        #     session=db_session, team_id=eave_team.id
        # )
        # if github_installation:
        #     eave_team.integrations.append(eave.stdlib.core_api.enums.Integration.github)

        atlassian_installation = (
            await eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm.one_or_none(
                session=db_session, team_id=eave_team.id
            )
        )
        if atlassian_installation:
            eave_team.integrations.append(eave.stdlib.core_api.enums.Integration.atlassian)

    eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_state.eave_account)

    return eave.stdlib.core_api.operations.GetAuthenticatedAccount.ResponseBody(
        account=eave_account,
        team=eave_team,
    )


async def get_authed_account_team(
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.GetAuthenticatedAccountTeam.ResponseBody:
    eave_state = eave.core.public.requests.util.get_eave_state(request=request)
    logger.info("authed_account.get_authed_account_team", extra=eave_state.log_context)

    eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_state.eave_team)
    eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_state.eave_account)

    eave_team.integrations = []

    async with eave.core.internal.database.async_session.begin() as db_session:
        slack_installation = await eave.core.internal.orm.slack_installation.SlackInstallationOrm.one_or_none(
            session=db_session, team_id=eave_team.id
        )
        if slack_installation:
            eave_team.integrations.append(eave.stdlib.core_api.enums.Integration.slack)

        # github_installation = await eave.core.internal.orm.slack_installation.GithubInstallationOrm.one_or_none(
        #     session=db_session, team_id=eave_team.id
        # )
        # if github_installation:
        #     eave_team.integrations.append(eave.stdlib.core_api.enums.Integration.github)

        atlassian_installation = (
            await eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm.one_or_none(
                session=db_session, team_id=eave_team.id
            )
        )
        if atlassian_installation:
            eave_team.integrations.append(eave.stdlib.core_api.enums.Integration.atlassian)

    return eave.stdlib.core_api.operations.GetAuthenticatedAccountTeam.ResponseBody(
        account=eave_account,
        team=eave_team,
        integrations=eave.stdlib.core_api.models.Integrations(
            slack=eave.stdlib.core_api.models.SlackInstallation.from_orm(slack_installation),
            github=None,  # eave.stdlib.core_api.models.GithubInstallation.from_orm(github_installation),
            atlassian=eave.stdlib.core_api.models.AtlassianInstallation.from_orm(atlassian_installation),
        ),
    )
