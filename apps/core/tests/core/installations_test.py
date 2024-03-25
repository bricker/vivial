from http import HTTPStatus

import eave.core.internal.orm.github_installation
import eave.core.internal.orm.team
from eave.stdlib.core_api.models.error import ErrorResponse
from eave.stdlib.core_api.models.github_installation import GithubInstallationQueryInput
from eave.stdlib.core_api.operations.github_installation import QueryGithubInstallation

from .base import BaseTestCase


class TestInstallationsRequests(BaseTestCase):
    async def test_get_github_installation(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            await eave.core.internal.orm.github_installation.GithubInstallationOrm.create(
                session=s,
                team_id=team.id,
                github_install_id=self.anystr("github_install_id"),
            )

        response = await self.make_request(
            path=QueryGithubInstallation.config.path,
            payload=QueryGithubInstallation.RequestBody(
                github_installation=GithubInstallationQueryInput(
                    github_install_id=self.anystr("github_install_id"),
                ),
            ),
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = QueryGithubInstallation.ResponseBody(**response.json())

        assert response_obj.github_installation.github_install_id == self.anystr("github_install_id")

    async def test_get_github_installation_not_found(self) -> None:
        response = await self.make_request(
            path=QueryGithubInstallation.config.path,
            payload=QueryGithubInstallation.RequestBody(
                github_installation=GithubInstallationQueryInput(
                    github_install_id=self.anystr("github_install_id"),
                ),
            ),
        )

        response_obj = ErrorResponse(**response.json())
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response_obj.status_code == HTTPStatus.NOT_FOUND
        assert response_obj.error_message == "Not Found"
