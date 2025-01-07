from httpx import Response

from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from eave.core.orm.account import AccountOrm

from ..base import BaseTestCase


class TestLoginMutation(BaseTestCase):
    async def _make_request(self, email: str, plaintext_password: str) -> Response:
        response = await self.make_graphql_request(
            "login",
            {
                "input": {
                    "email": email,
                    "plaintextPassword": plaintext_password,
                },
            },
        )

        return response

    async def test_login_with_valid_credentials(self) -> None:
        async with self.db_session.begin() as session:
            account_orm = AccountOrm(
                session,
                email=self.anyemail("email"),
                plaintext_password=self.anystr("plaintext_password"),
                visitor_id=None,
            )
            account_orm.last_login = self.anydatetime("last_login", past=True)

        response = await self._make_request(
            email=self.getemail("email"), plaintext_password=self.getstr("plaintext_password")
        )
        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["login"]

        assert data["__typename"] == "LoginSuccess"
        assert data["account"]["id"] == str(account_orm.id)
        assert data["account"]["email"] == account_orm.email

        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) is not None
        assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) is not None
        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) != response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

        async with self.db_session.begin() as session:
            updated_account_orm = await AccountOrm.get_one(session, account_orm.id)
            assert updated_account_orm.last_login is not None and updated_account_orm.last_login > self.getdatetime(
                "last_login"
            )

    async def test_login_with_incorrect_password(self) -> None:
        async with self.db_session.begin() as session:
            account_orm = AccountOrm(
                session,
                email=self.anyemail("email"),
                plaintext_password=self.anystr("plaintext_password"),
                visitor_id=self.anystr(),
            )
            account_orm.last_login = self.anydatetime("last_login", past=True)

        response = await self._make_request(
            email=self.getemail("email"), plaintext_password=self.anystr("incorrect password")
        )
        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["login"]

        assert data["__typename"] == "LoginFailure"
        assert "account" not in data
        assert data["failureReason"] == "INVALID_CREDENTIALS"

        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) is None
        assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) is None

        async with self.db_session.begin() as session:
            updated_account_orm = await AccountOrm.get_one(session, account_orm.id)
            assert updated_account_orm.last_login is not None and updated_account_orm.last_login == self.getdatetime(
                "last_login"
            )

    async def test_login_with_non_existent_account(self) -> None:
        async with self.db_session.begin() as session:
            account_orm = AccountOrm(
                session,
                email=self.anyemail("email"),
                plaintext_password=self.anystr("plaintext_password"),
                visitor_id=self.anystr(),
            )
            account_orm.last_login = self.anydatetime("last_login", past=True)

        response = await self._make_request(
            email=self.anyemail("some other email"), plaintext_password=self.getstr("plaintext_password")
        )
        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["login"]

        assert data["__typename"] == "LoginFailure"
        assert "account" not in data
        assert data["failureReason"] == "INVALID_CREDENTIALS"

        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) is None
        assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) is None

        async with self.db_session.begin() as session:
            updated_account_orm = await AccountOrm.get_one(session, account_orm.id)
            assert updated_account_orm.last_login is not None and updated_account_orm.last_login == self.getdatetime(
                "last_login"
            )

    async def test_login_with_empty_password(self) -> None:
        async with self.db_session.begin() as session:
            account_orm = AccountOrm(
                session,
                email=self.anyemail("email"),
                plaintext_password=self.anystr("plaintext_password"),
                visitor_id=None,
            )

            account_orm.last_login = self.anydatetime("last_login", past=True)

        response = await self._make_request(email=self.anyemail("some other email"), plaintext_password="")
        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["login"]

        assert data["__typename"] == "LoginFailure"
        assert "account" not in data
        assert data["failureReason"] == "INVALID_CREDENTIALS"

        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) is None
        assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) is None

        async with self.db_session.begin() as session:
            updated_account_orm = await AccountOrm.get_one(session, account_orm.id)
            assert updated_account_orm.last_login is not None and updated_account_orm.last_login == self.getdatetime(
                "last_login"
            )
