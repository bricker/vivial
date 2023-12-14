from http import HTTPStatus
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.stdlib.core_api.models.github_repos import (
    GithubRepoCreateInput,
    GithubRepoFeature,
    GithubRepoFeatureState,
    GithubRepoListInput,
    GithubRepoUpdateInput,
    GithubRepoUpdateValues,
    GithubReposDeleteInput,
    GithubReposFeatureStateInput,
)
from eave.stdlib.core_api.operations.github_repos import (
    CreateGithubRepoRequest,
    DeleteGithubReposRequest,
    FeatureStateGithubReposRequest,
    GetAllTeamsGithubReposRequest,
    GetGithubReposRequest,
    UpdateGithubReposRequest,
)

from .base import BaseTestCase


class TestGithubRepoRequests(BaseTestCase):
    async def _create_repos(self, session: AsyncSession, team_id: UUID, quantity: int = 5) -> list[GithubRepoOrm]:
        orms: list[GithubRepoOrm] = []
        gh_install = await GithubInstallationOrm.create(
            session=session,
            team_id=team_id,
            github_install_id=self.anystr(),
        )

        for i in range(quantity):
            orms.append(
                await GithubRepoOrm.create(
                    session=session,
                    team_id=team_id,
                    external_repo_id=self.anystr(f"external_repo_id:{team_id}:{i}"),
                    display_name=self.anystr(),
                    github_installation_id=gh_install.id,
                )
            )
        return orms

    async def test_get_all_teams_repos_with_api_doc_feature_enabled(self) -> None:
        async with self.db_session.begin() as s:
            team1 = await self.make_team(s)
            team2 = await self.make_team(s)

            # create 10 GithubRepoOrm
            orms1 = await self._create_repos(session=s, team_id=team1.id, quantity=5)
            orms2 = await self._create_repos(session=s, team_id=team2.id, quantity=5)

            # set 2 to DISABLED, so the expected response contains only 8 repos
            orms1[0].api_documentation_state = GithubRepoFeatureState.DISABLED
            orms2[0].api_documentation_state = GithubRepoFeatureState.DISABLED

        response = await self.make_request(
            path=GetAllTeamsGithubReposRequest.config.path,
            payload=GetAllTeamsGithubReposRequest.RequestBody(
                query_params=GithubReposFeatureStateInput(
                    feature=GithubRepoFeature.API_DOCUMENTATION,
                    state=GithubRepoFeatureState.ENABLED,
                ),
            ),
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetAllTeamsGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 8

        response = await self.make_request(
            path=GetAllTeamsGithubReposRequest.config.path,
            payload=GetAllTeamsGithubReposRequest.RequestBody(
                query_params=GithubReposFeatureStateInput(
                    feature=GithubRepoFeature.API_DOCUMENTATION,
                    state=GithubRepoFeatureState.DISABLED,
                ),
            ),
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetAllTeamsGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 2

    async def test_get_all_teams_repos_with_inline_code_doc_feature_enabled(self) -> None:
        async with self.db_session.begin() as s:
            team1 = await self.make_team(s)
            team2 = await self.make_team(s)
            orms1 = await self._create_repos(session=s, team_id=team1.id, quantity=5)
            orms2 = await self._create_repos(session=s, team_id=team2.id, quantity=5)

            orms1[0].inline_code_documentation_state = GithubRepoFeatureState.DISABLED
            orms2[0].inline_code_documentation_state = GithubRepoFeatureState.DISABLED

        response = await self.make_request(
            path=GetAllTeamsGithubReposRequest.config.path,
            payload=GetAllTeamsGithubReposRequest.RequestBody(
                query_params=GithubReposFeatureStateInput(
                    feature=GithubRepoFeature.INLINE_CODE_DOCUMENTATION,
                    state=GithubRepoFeatureState.ENABLED,
                ),
            ),
            team_id=team2.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetAllTeamsGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 8

        response = await self.make_request(
            path=GetAllTeamsGithubReposRequest.config.path,
            payload=GetAllTeamsGithubReposRequest.RequestBody(
                query_params=GithubReposFeatureStateInput(
                    feature=GithubRepoFeature.INLINE_CODE_DOCUMENTATION,
                    state=GithubRepoFeatureState.DISABLED,
                ),
            ),
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetAllTeamsGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 2

    async def test_get_all_teams_repos_with_arch_doc_feature_enabled(self) -> None:
        async with self.db_session.begin() as s:
            team1 = await self.make_team(s)
            team2 = await self.make_team(s)
            orms1 = await self._create_repos(session=s, team_id=team1.id, quantity=5)
            orms2 = await self._create_repos(session=s, team_id=team2.id, quantity=5)

            orms1[0].architecture_documentation_state = GithubRepoFeatureState.DISABLED
            orms2[0].architecture_documentation_state = GithubRepoFeatureState.DISABLED

        response = await self.make_request(
            path=GetAllTeamsGithubReposRequest.config.path,
            payload=GetAllTeamsGithubReposRequest.RequestBody(
                query_params=GithubReposFeatureStateInput(
                    feature=GithubRepoFeature.ARCHITECTURE_DOCUMENTATION,
                    state=GithubRepoFeatureState.ENABLED,
                ),
            ),
            team_id=team2.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetAllTeamsGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 8

        response = await self.make_request(
            path=GetAllTeamsGithubReposRequest.config.path,
            payload=GetAllTeamsGithubReposRequest.RequestBody(
                query_params=GithubReposFeatureStateInput(
                    feature=GithubRepoFeature.ARCHITECTURE_DOCUMENTATION,
                    state=GithubRepoFeatureState.DISABLED,
                ),
            ),
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetAllTeamsGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 2

    async def test_github_repo_req_get_one(self) -> None:
        async with self.db_session.begin() as s:
            team1 = await self.make_team(s)
            team2 = await self.make_team(s)
            await self._create_repos(session=s, team_id=team1.id)
            await self._create_repos(session=s, team_id=team2.id)
            account = await self.make_account(s, team_id=team2.id)

        response = await self.make_request(
            path=GetGithubReposRequest.config.path,
            payload=GetGithubReposRequest.RequestBody(
                repos=[
                    GithubRepoListInput(
                        external_repo_id=self.getstr(f"external_repo_id:{team2.id}:3"),
                    ),
                ],
            ),
            team_id=team2.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 1
        assert response_obj.repos[0].team_id == team2.id
        assert response_obj.repos[0].external_repo_id == self.getstr(f"external_repo_id:{team2.id}:3")

    async def test_github_repo_req_get_many_by_team(self) -> None:
        async with self.db_session.begin() as s:
            team1 = await self.make_team(s)
            team2 = await self.make_team(s)
            await self._create_repos(session=s, team_id=team1.id)
            await self._create_repos(session=s, team_id=team2.id)
            account = await self.make_account(s, team_id=team2.id)

        response = await self.make_request(
            path=GetGithubReposRequest.config.path,
            payload=GetGithubReposRequest.RequestBody(repos=None),
            team_id=team2.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 5
        assert all(
            map(lambda repo: repo.team_id == team2.id, response_obj.repos)
        ), "Not all repos associate with expected team"

    async def test_github_repo_req_create(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            await GithubInstallationOrm.create(
                session=s,
                team_id=team.id,
                github_install_id=self.anystr(),
            )

        response = await self.make_request(
            path=CreateGithubRepoRequest.config.path,
            payload=CreateGithubRepoRequest.RequestBody(
                repo=GithubRepoCreateInput(
                    external_repo_id=self.anystr("external_repo_id"),
                    display_name=self.anystr(),
                    inline_code_documentation_state=GithubRepoFeatureState.DISABLED,
                ),
            ),
            team_id=team.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = CreateGithubRepoRequest.ResponseBody(**response.json())
        assert response_obj.repo.team_id == team.id
        assert response_obj.repo.external_repo_id == self.getstr("external_repo_id")
        assert response_obj.repo.inline_code_documentation_state == GithubRepoFeatureState.DISABLED
        assert response_obj.repo.architecture_documentation_state == GithubRepoFeatureState.ENABLED
        assert response_obj.repo.api_documentation_state == GithubRepoFeatureState.ENABLED

    async def test_github_repo_req_update(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            orms = await self._create_repos(session=s, team_id=team.id)
            account = await self.make_account(s, team_id=team.id)

        response = await self.make_request(
            path=UpdateGithubReposRequest.config.path,
            payload=UpdateGithubReposRequest.RequestBody(
                repos=[
                    GithubRepoUpdateInput(
                        id=repo.id,
                        new_values=GithubRepoUpdateValues(
                            inline_code_documentation_state=GithubRepoFeatureState.PAUSED,
                        ),
                    )
                    for repo in orms
                ]
            ),
            team_id=team.id,
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = UpdateGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 5
        assert all(
            repo.inline_code_documentation_state == GithubRepoFeatureState.PAUSED for repo in response_obj.repos
        ), "Not all ORM objects got the updated value"

    async def test_github_repo_req_delete(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            orms = await self._create_repos(session=s, team_id=team.id, quantity=5)
            account = await self.make_account(s, team_id=team.id)

        response = await self.make_request(
            path=DeleteGithubReposRequest.config.path,
            payload=DeleteGithubReposRequest.RequestBody(
                repos=[GithubReposDeleteInput(id=repo.id) for repo in orms[:2]]
            ),
            team_id=team.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK

        # check the correct number were deleted

        response = await self.make_request(
            path=GetGithubReposRequest.config.path,
            payload=GetGithubReposRequest.RequestBody(repos=None),
            team_id=team.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 3

    async def test_github_repo_req_feature_state_query(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            orms = await self._create_repos(session=s, team_id=team.id)
            orms[1].inline_code_documentation_state = GithubRepoFeatureState.DISABLED
            account = await self.make_account(s, team_id=team.id)

        # all entries should all have matching API_DOCUMENTATION feature state

        response = await self.make_request(
            path=FeatureStateGithubReposRequest.config.path,
            payload=FeatureStateGithubReposRequest.RequestBody(
                query_params=GithubReposFeatureStateInput(
                    feature=GithubRepoFeature.API_DOCUMENTATION,
                    state=GithubRepoFeatureState.ENABLED,
                )
            ),
            team_id=team.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = FeatureStateGithubReposRequest.ResponseBody(**response.json())
        assert response_obj.states_match is True

        # all entries should not all have matching INLINE_CODE_DOCUMENTATION feature state

        response = await self.make_request(
            path=FeatureStateGithubReposRequest.config.path,
            payload=FeatureStateGithubReposRequest.RequestBody(
                query_params=GithubReposFeatureStateInput(
                    feature=GithubRepoFeature.INLINE_CODE_DOCUMENTATION,
                    state=GithubRepoFeatureState.ENABLED,
                ),
            ),
            team_id=team.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = FeatureStateGithubReposRequest.ResponseBody(**response.json())
        assert response_obj.states_match is False
