from http import HTTPStatus

from eave.stdlib.core_api.operations.status import Status
from eave.stdlib.core_api.operations.team import GetTeamRequest
from eave.stdlib.headers import EAVE_SIGNATURE_HEADER, EAVE_TEAM_ID_HEADER

from .base import BaseTestCase


class TestSignatureVerification(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(session=s)

    async def test_signature_bypass(self) -> None:
        response = await self.make_request(
            method=Status.config.method,
            path=Status.config.path,
            headers={EAVE_SIGNATURE_HEADER: None},
        )

        assert response.status_code == HTTPStatus.OK
        assert self.get_mock("eave.stdlib.signing.verify_signature_or_exception").call_count == 0

    async def test_missing_signature_header(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            team_id=self._team.id,
            headers={
                EAVE_SIGNATURE_HEADER: None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert self.get_mock("eave.stdlib.signing.verify_signature_or_exception").call_count == 0

    async def test_mismatched_signature(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            team_id=self._team.id,
            headers={
                EAVE_SIGNATURE_HEADER: self.anystr("mismatched signature"),
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert self.get_mock("eave.stdlib.signing.verify_signature_or_exception").call_count == 1

    async def test_signature_with_team_id(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self._team.id),
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert self.get_mock("eave.stdlib.signing.verify_signature_or_exception").call_count == 1
