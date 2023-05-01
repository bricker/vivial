import eave.core.internal.database as eave_db
import eave.core.internal.orm.github_installation
import eave.stdlib.core_api.models as models
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.core.internal.orm.team import TeamOrm


async def query(
    input: eave_ops.GetGithubInstallation.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.GetGithubInstallation.ResponseBody:
    async with eave_db.async_session.begin() as db_session:
        github_installation = await eave.core.internal.orm.github_installation.GithubInstallationOrm.one_or_exception(
            session=db_session,
            github_install_id=input.github_installation.github_install_id,
        )

        team = await TeamOrm.one_or_exception(session=db_session, team_id=github_installation.team_id)

        return eave_ops.GetGithubInstallation.ResponseBody(
            github_installation=models.GithubInstallation.from_orm(github_installation), team=models.Team.from_orm(team)
        )
