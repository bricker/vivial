import time
from datetime import datetime
from http import HTTPStatus

import eave.core.internal.database as eave_db
from eave.core.internal.orm.auth_token import AuthTokenOrm
import eave.stdlib.core_api.enums as eave_enums
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.signing as eave_signing
import eave.stdlib.util as eave_util
import mockito
import pytest
from sqlalchemy import select

from .base import BaseTestCase


class TestAuthRequests(BaseTestCase):
    async def test_request_access_token(self) -> None:
        account = await self.make_account()

        assert (await self.count(AuthTokenOrm)) == 0

        response = await self.make_request(
            url="/auth/token/request",
            payload={
                "exchange_offer": {
                    "auth_provider": account.auth_provider,
                    "auth_id": account.auth_id,
                    "oauth_token": account.oauth_token,
                }
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert (await self.count(AuthTokenOrm)) == 1

        response_obj = eave_ops.RequestAccessToken.ResponseBody(**response.json())

        async with eave_db.async_session.begin() as db_session:
            token = await db_session.scalar(
                select(AuthTokenOrm)
                .where(AuthTokenOrm.access_token_hashed == eave_util.sha256hexdigest(response_obj.access_token))
                .where(AuthTokenOrm.refresh_token_hashed == eave_util.sha256hexdigest(response_obj.refresh_token))
            )

        assert token is not None
        assert token.account_id == account.id
        assert token.team_id == account.team_id
        assert token.iss == "eave_api"
        assert token.aud == "eave_www"
        assert token.invalidated is None
        assert token.expires.timestamp() == pytest.approx(time.time() + (60 * 10), abs=1)
        assert token.expired is False

    async def test_request_access_token_with_invalid_offer(self) -> None:
        await self.make_account()
        assert (await self.count(AuthTokenOrm)) == 0

        response = await self.make_request(
            url="/auth/token/request",
            payload={
                "exchange_offer": {
                    "auth_provider": eave_enums.AuthProvider.slack,
                    "auth_id": self.anystring("auth_id_invalid"),
                    "oauth_token": self.anystring("oauth_token_invalid"),
                }
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.text == ""
        assert (await self.count(AuthTokenOrm)) == 0

    async def test_refresh_access_token(self) -> None:
        account = await self.make_account()

        assert (await self.count(AuthTokenOrm)) == 0
        old_access_token, old_refresh_token, old_auth_token_orm = await self.mock_auth_token(account=account)

        response = await self.make_request(
            url="/auth/token/refresh",
            access_token=old_access_token,
            payload={
                "access_token": str(old_access_token),
                "refresh_token": str(old_refresh_token),
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert (await self.count(AuthTokenOrm)) == 1  # The old one gets immediately deleted, so only one
        assert (await self.reload(old_auth_token_orm)) is None

        response_obj = eave_ops.RequestAccessToken.ResponseBody(**response.json())
        assert response_obj.access_token
        assert response_obj.access_token != old_access_token
        assert response_obj.refresh_token
        assert response_obj.refresh_token != old_refresh_token

        async with eave_db.async_session.begin() as db_session:
            token = await db_session.scalar(
                select(AuthTokenOrm)
                .where(AuthTokenOrm.access_token_hashed == eave_util.sha256hexdigest(response_obj.access_token))
                .where(AuthTokenOrm.refresh_token_hashed == eave_util.sha256hexdigest(response_obj.refresh_token))
            )

        assert token is not None
        assert token  # for type hints
        assert token.account_id == account.id
        assert token.team_id == account.team_id
        assert token.iss == "eave_api"
        assert token.aud == "eave_www"
        assert token.invalidated is None
        # assert that the token expiration is approximately 10 minutes in the future (accounting for test latency)
        assert token.expires.timestamp() == pytest.approx(time.time() + (60 * 10), abs=1)
        assert token.expired is False

    async def test_refresh_access_token_with_not_found_tokens(self) -> None:
        account = await self.make_account()

        at1, rt1, orm1 = await self.mock_auth_token(account=account)

        # Delete the token to mock the scenario where a token was refreshed and deleted, and then used again.
        await self.delete(orm1)

        response = await self.make_request(
            url="/auth/token/refresh",
            access_token=at1,
            payload={
                "access_token": str(at1),
                "refresh_token": str(rt1),
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_refresh_access_token_with_mismatched_tokens(self) -> None:
        account = await self.make_account()

        assert (await self.count(AuthTokenOrm)) == 0
        at1, rt1, orm1 = await self.mock_auth_token(account=account)
        at2, rt2, orm2 = await self.mock_auth_token(account=account)

        response = await self.make_request(
            url="/auth/token/refresh",
            access_token=at1,
            payload={
                "access_token": str(at1),
                "refresh_token": str(rt2),
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert (await self.count(AuthTokenOrm)) == 2

    async def test_refresh_access_token_with_invalid_token(self) -> None:
        account = await self.make_account()

        assert (await self.count(AuthTokenOrm)) == 0
        at1, rt1, orm1 = await self.mock_auth_token(account=account)

        response = await self.make_request(
            url="/auth/token/refresh",
            access_token=at1,
            payload={
                "access_token": "sdfdsfsd",
                "refresh_token": "sdfsfs",
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert (await self.count(AuthTokenOrm)) == 1

    async def test_refresh_access_token_with_invalidated_tokens(self) -> None:
        account = await self.make_account()

        assert (await self.count(AuthTokenOrm)) == 0
        at1, rt1, orm1 = await self.mock_auth_token(account=account)

        orm1.invalidated = datetime.utcnow()
        await self.save(orm1)

        response = await self.make_request(
            url="/auth/token/refresh",
            access_token=at1,
            payload={
                "access_token": str(at1),
                "refresh_token": str(rt1),
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_refresh_access_token_with_not_found_account(self) -> None:
        # This scenario is impossible because of the foreign key constraint on AuthToken -> Account.
        # An account can't be deleted if there are associated AuthTokens.
        # This should be changed so that deleting an Account cascades to its AuthTokens.
        # Regardless, there should (reasonably) never be scenario where a valid auth token is passed for an account that
        # has been deleted.
        assert True

        # Here's what the test would look like if this scenario was possible:
        # account = await self.make_account()

        # assert (await self.count(AuthTokenOrm)) == 0
        # at1, rt1, orm1 = await self.mock_auth_token(account=account)

        # # The account was deleted, therefore the tokens should be implicitly invalid.
        # # Probably the tokens should be deleted in a database cascade operation anyways.
        # await self.delete(account)

        # response = await self.make_request(
        #     url="/auth/token/refresh",
        #     access_token=at1,
        #     payload={
        #         "access_token": str(at1),
        #         "refresh_token": str(rt1),
        #     },
        # )

        # assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_auth_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            url="/status",
        )

        assert response.status_code == HTTPStatus.OK
        mockito.verify(eave_signing, times=0).verify_signature_or_exception(...)
        mockito.verify(eave_signing, times=0).sign_b64(...)
