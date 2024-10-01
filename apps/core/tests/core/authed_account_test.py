from http import HTTPStatus

from eave.stdlib.core_api.operations.account import GetMyAccountRequest

from .base import BaseTestCase


class TestAuthedAccountRequests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_get_authed_account(self) -> None:
        async with self.db_session.begin() as s:
            account = await self.make_account(s)

        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            payload=None,
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK

        response_obj = GetMyAccountRequest.ResponseBody(**response.json())

        assert response_obj.account.email == account.email
