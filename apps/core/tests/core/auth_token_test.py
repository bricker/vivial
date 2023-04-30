from datetime import datetime

import eave.core.internal.database as eave_db
import sqlalchemy.exc
from eave.core.internal.orm.auth_token import AuthTokenOrm
from eave.stdlib.eave_origins import EaveOrigin

from .base import BaseTestCase


class TestAuthTokenOrm(BaseTestCase):
    async def test_find_without_expired(self) -> None:
        account = await self.make_account()
        access_token, refresh_token, auth_token_orm = await self.mock_auth_token(account=account)

        auth_token_orm.expires = datetime(year=1846, month=9, day=23)
        await self.save(auth_token_orm)

        with self.assertRaises(sqlalchemy.exc.NoResultFound):
            async with eave_db.async_session.begin() as db_session:
                await AuthTokenOrm.one_or_exception(
                    session=db_session,
                    log_context={},
                    access_token=str(access_token),
                    aud=EaveOrigin.eave_www.value,
                    allow_expired=False,
                )

    async def test_find_include_expired(self) -> None:
        account = await self.make_account()
        access_token, refresh_token, auth_token_orm = await self.mock_auth_token(account=account)

        auth_token_orm.expires = datetime(year=1846, month=9, day=23)
        await self.save(auth_token_orm)

        async with eave_db.async_session.begin() as db_session:
            result = await AuthTokenOrm.one_or_exception(
                session=db_session,
                log_context={},
                access_token=str(access_token),
                aud=EaveOrigin.eave_www.value,
                allow_expired=True,
            )

        # Really this test is just validating that no error is thrown
        assert result

    async def test_expired(self) -> None:
        auth_token = AuthTokenOrm(expires=datetime(year=1846, month=9, day=23))
        assert auth_token.expired is True

        now = datetime.utcnow()
        auth_token = AuthTokenOrm(expires=datetime(year=now.year + 1, month=now.month, day=now.day))
        assert auth_token.expired is False

    async def test_find_and_verify_with_team_or_exception(self) -> None:
        pass
