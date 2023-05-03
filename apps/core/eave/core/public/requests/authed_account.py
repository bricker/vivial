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


async def get_authed_account(
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.GetAuthenticatedAccount.ResponseBody:
    eave_state = eave.core.public.requests.util.get_eave_state(request=request)
    eave_account_orm = eave_state.eave_account
    eave_team_orm = eave_state.eave_team

    eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
    eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_account_orm)

    return eave.stdlib.core_api.operations.GetAuthenticatedAccount.ResponseBody(
        account=eave_account,
        team=eave_team,
    )


async def get_authed_account_team_integrations(
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody:
    eave_state = eave.core.public.requests.util.get_eave_state(request=request)
    eave_account_orm = eave_state.eave_account
    eave_team_orm = eave_state.eave_team

    async with eave.core.internal.database.async_session.begin() as db_session:
        integrations = await eave_team_orm.get_integrations(session=db_session)

    eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
    eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_account_orm)

    return eave.stdlib.core_api.operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(
        account=eave_account,
        team=eave_team,
        integrations=integrations,
    )

async def update_atlassian_integration(
    input: eave.stdlib.core_api.operations.UpdateAtlassianInstallation.RequestBody,
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.UpdateAtlassianInstallation.ResponseBody:
    eave_state = eave.core.public.requests.util.get_eave_state(request=request)
    eave_account_orm = eave_state.eave_account
    eave_team_orm = eave_state.eave_team

    async with eave.core.internal.database.async_session.begin() as db_session:
        installation = await eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm.one_or_exception(
            session=db_session,
            team_id=eave_team_orm.id,
        )

        if input.atlassian_integration.confluence_space_key is not None:
            installation.confluence_space_key = input.atlassian_integration.confluence_space_key

    eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
    eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_account_orm)
    atlassian_integration = eave.stdlib.core_api.models.AtlassianInstallation.from_orm(installation)

    return eave.stdlib.core_api.operations.UpdateAtlassianInstallation.ResponseBody(
        account=eave_account,
        team=eave_team,
        atlassian_integration=atlassian_integration,
    )
