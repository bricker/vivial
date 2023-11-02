from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.github_repos import GithubRepoOrm
from .base import BaseTestCase


class TestGithubReposOrm(BaseTestCase):
    async def test_query_sorting(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            gh_installation_orm = await GithubInstallationOrm.create(
                session=s,
                team_id=team.id,
                github_install_id=self.anystr(),
            )

            for repo_name in list("zamboni"):
                await GithubRepoOrm.create(
                    session=s,
                    team_id=team.id,
                    display_name=repo_name,
                    github_installation_id=gh_installation_orm.id,
                    external_repo_id=self.anystr(),
                )

            orms = await GithubRepoOrm.query(session=s, params=GithubRepoOrm.QueryParams(team_id=team.id))

        assert list(map(lambda r: r.display_name, orms)) == list("abimnoz")
