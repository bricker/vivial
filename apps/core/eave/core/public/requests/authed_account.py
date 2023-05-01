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
    eave_team_orm = eave_state.eave_team

    async with eave.core.internal.database.async_session.begin() as db_session:
        integrations, integrations_list = await eave_team_orm.get_integrations(session=db_session)

    eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
    eave_team.integrations = integrations_list

    eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_state.eave_account)

    return eave.stdlib.core_api.operations.GetAuthenticatedAccount.ResponseBody(
        account=eave_account,
        team=eave_team,
    )


async def get_authed_account_team(
    request: fastapi.Request,
) -> eave.stdlib.core_api.operations.GetAuthenticatedAccountTeam.ResponseBody:
    eave_state = eave.core.public.requests.util.get_eave_state(request=request)
    eave_team_orm = eave_state.eave_team

    async with eave.core.internal.database.async_session.begin() as db_session:
        integrations, integrations_list = await eave_team_orm.get_integrations(session=db_session)

    eave_team = eave.stdlib.core_api.models.Team.from_orm(eave_team_orm)
    eave_team.integrations = integrations_list

    eave_account = eave.stdlib.core_api.models.AuthenticatedAccount.from_orm(eave_state.eave_account)

    return eave.stdlib.core_api.operations.GetAuthenticatedAccountTeam.ResponseBody(
        account=eave_account,
        team=eave_team,
        integrations=integrations,
    )
