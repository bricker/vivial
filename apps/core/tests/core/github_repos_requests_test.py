from http import HTTPStatus
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.stdlib.core_api.models.github_repos import (
    Feature,
    State,
)
from eave.stdlib.core_api.operations.github_repos import (
    CreateGithubRepoRequest,
    FeatureStateGithubReposRequest,
    GetGithubReposRequest,
    UpdateGithubReposRequest,
)

from .base import BaseTestCase


class TestGithubRepoRequests(BaseTestCase):
    async def create_repos(self, session: AsyncSession, team_id: UUID, quantity: int = 5) -> list[GithubRepoOrm]:
        orms: list[GithubRepoOrm] = []
        for i in range(quantity):
            orms.append(
                await GithubRepoOrm.create(
                    session=session,
                    team_id=team_id,
                    external_repo_id=self.anystr(f"external_repo_id:{team_id}:{i}"),
                    display_name=self.anystr(),
                )
            )
        return orms

    async def test_github_repo_req_get_one(self) -> None:
        async with self.db_session.begin() as s:
            team1 = await self.make_team(s)
            team2 = await self.make_team(s)
            await self.create_repos(session=s, team_id=team1.id)
            await self.create_repos(session=s, team_id=team2.id)
            account = await self.make_account(s, team_id=team2.id)

        response = await self.make_request(
            path="/github-repos/query",
            payload={
                "repos": [
                    {
                        "external_repo_id": self.getstr(f"external_repo_id:{team2.id}:3"),
                    },
                ]
            },
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
            await self.create_repos(session=s, team_id=team1.id)
            await self.create_repos(session=s, team_id=team2.id)
            account = await self.make_account(s, team_id=team2.id)

        response = await self.make_request(
            path="/github-repos/query",
            payload={"repos": None},
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
            account = await self.make_account(s, team_id=team.id)

        response = await self.make_request(
            path="/github-repos/create",
            payload={
                "repo": {
                    "external_repo_id": self.anystr("external_repo_id"),
                    "inline_code_documentation_state": State.ENABLED.value,
                }
            },
            team_id=team.id,
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = CreateGithubRepoRequest.ResponseBody(**response.json())
        assert response_obj.repo.team_id == team.id
        assert response_obj.repo.external_repo_id == self.getstr("external_repo_id")
        assert response_obj.repo.inline_code_documentation_state == State.ENABLED
        assert response_obj.repo.architecture_documentation_state == State.DISABLED
        assert response_obj.repo.api_documentation_state == State.DISABLED

    async def test_github_repo_req_update(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            await self.create_repos(session=s, team_id=team.id)
            account = await self.make_account(s, team_id=team.id)

        response = await self.make_request(
            path="/github-repos/update",
            payload={
                "repos": [
                    {
                        "external_repo_id": self.getstr(f"external_repo_id:{team.id}:{i}"),
                        "new_values": {
                            "inline_code_documentation_state": State.PAUSED.value,
                        },
                    }
                    for i in range(2)
                ]
            },
            team_id=team.id,
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = UpdateGithubReposRequest.ResponseBody(**response.json())
        assert len(response_obj.repos) == 2
        assert all(
            map(lambda repo: repo.inline_code_documentation_state == State.PAUSED, response_obj.repos)
        ), "Not all ORM objects got the updated value"

    async def test_github_repo_req_delete(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            await self.create_repos(session=s, team_id=team.id)
            account = await self.make_account(s, team_id=team.id)

        response = await self.make_request(
            path="/github-repos/delete",
            payload={
                "repos": [{"external_repo_id": self.getstr(f"external_repo_id:{team.id}:{i}")} for i in range(2)],
            },
            team_id=team.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK

        # check the correct number were deleted

        response = await self.make_request(
            path="/github-repos/query",
            payload={"repos": None},
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
            orms = await self.create_repos(session=s, team_id=team.id)
            orms[1].inline_code_documentation_state = State.ENABLED
            account = await self.make_account(s, team_id=team.id)

        # all entries should all have matching API_DOCUMENTATION feature state

        response = await self.make_request(
            path="/github-repos/query/enabled",
            payload={
                "query_params": {
                    "feature": Feature.API_DOCUMENTATION.value,
                    "state": State.DISABLED.value,
                }
            },
            team_id=team.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = FeatureStateGithubReposRequest.ResponseBody(**response.json())
        assert response_obj.states_match is True

        # all entries should not all have matching INLINE_CODE_DOCUMENTATION feature state

        response = await self.make_request(
            path="/github-repos/query/enabled",
            payload={
                "query_params": {
                    "feature": Feature.INLINE_CODE_DOCUMENTATION.value,
                    "state": State.ENABLED.value,
                }
            },
            team_id=team.id,
            access_token=account.access_token,
            account_id=account.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = FeatureStateGithubReposRequest.ResponseBody(**response.json())
        assert response_obj.states_match is False
