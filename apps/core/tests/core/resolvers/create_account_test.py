from uuid import UUID

from httpx import Response

from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from eave.core.orm.account import AccountOrm
from eave.stdlib.analytics import SEGMENT_ANONYMOUS_ID_COOKIE_NAME

from ..base import BaseTestCase


class TestCreateAccountMutation(BaseTestCase):
    async def _make_request(self, email: str | None = None, plaintext_password: str | None = None) -> Response:
        response = await self.make_graphql_request(
            "createAccount",
            {
                "input": {
                    "email": email if email is not None else self.anyemail("email"),
                    "plaintextPassword": plaintext_password
                    if plaintext_password is not None
                    else str(self.anyuuid("password")),
                },
            },
            cookies={
                SEGMENT_ANONYMOUS_ID_COOKIE_NAME: self.anystr("visitor id"),
            },
        )

        return response

    async def test_create_account_with_valid_input(self) -> None:
        assert self.get_mock("SendGridAPIClient.send").call_count == 0
        assert self.get_mock("segment.analytics.identify").call_count == 0
        assert self.get_mock("segment.analytics.track").call_count == 0

        response = await self._make_request()
        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["createAccount"]

        assert data["__typename"] == "CreateAccountSuccess"
        assert data["account"]["id"] is not None
        assert data["account"]["email"] == self.getemail("email")

        async with self.db_session.begin() as session:
            account_orm = await AccountOrm.get_one(session, UUID(data["account"]["id"]))
            assert account_orm.id == UUID(data["account"]["id"])
            assert account_orm.email == data["account"]["email"]
            assert account_orm.last_login is not None

        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) is not None
        assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) is not None
        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) != response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

        assert self.get_mock("SendGridAPIClient.send").call_count == 1

        assert self.get_mock("segment.analytics.identify").call_count == 1
        assert self.get_mock("segment.analytics.identify").call_args_list[0].kwargs["user_id"] == str(account_orm.id)
        assert self.get_mock("segment.analytics.identify").call_args_list[0].kwargs["anonymous_id"] == self.getstr(
            "visitor id"
        )

        assert self.get_mock("segment.analytics.track").call_count == 1
        assert self.get_mock("segment.analytics.track").call_args_list[0].kwargs["user_id"] == str(account_orm.id)
        assert self.get_mock("segment.analytics.track").call_args_list[0].kwargs["anonymous_id"] == self.getstr(
            "visitor id"
        )
        assert self.get_mock("segment.analytics.track").call_args_list[0].kwargs["event"] == "signup"

    async def test_create_account_with_weak_password(self) -> None:
        response = await self._make_request(plaintext_password="password")
        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["createAccount"]

        assert data["__typename"] == "CreateAccountFailure"
        assert data["failureReason"] == "WEAK_PASSWORD"
        assert data.get("validationErrors") is None

        async with self.db_session.begin() as session:
            count = await self.count(session, AccountOrm)
            assert count == 0

        assert ACCESS_TOKEN_COOKIE_NAME not in response.cookies
        assert REFRESH_TOKEN_COOKIE_NAME not in response.cookies
        assert self.get_mock("SendGridAPIClient.send").call_count == 0
        assert self.get_mock("segment.analytics.identify").call_count == 0
        assert self.get_mock("segment.analytics.track").call_count == 0

    async def test_create_account_with_invalid_email(self) -> None:
        response = await self._make_request(email="invalid_email")
        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["createAccount"]

        assert data["__typename"] == "CreateAccountFailure"
        assert data["failureReason"] == "VALIDATION_ERRORS"

        validation_errors = data["validationErrors"]
        assert len(validation_errors) == 1
        assert validation_errors[0]["field"] == "email"

        async with self.db_session.begin() as session:
            count = await self.count(session, AccountOrm)
            assert count == 0

        assert ACCESS_TOKEN_COOKIE_NAME not in response.cookies
        assert REFRESH_TOKEN_COOKIE_NAME not in response.cookies
        assert self.get_mock("SendGridAPIClient.send").call_count == 0
        assert self.get_mock("segment.analytics.identify").call_count == 0
        assert self.get_mock("segment.analytics.track").call_count == 0

    async def test_create_account_with_existing_account(self) -> None:
        async with self.db_session.begin() as session:
            account_orm = self.make_account(session)
            count = await self.count(session, AccountOrm)
            assert count == 1

        response = await self._make_request(email=account_orm.email)
        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["createAccount"]

        assert data["__typename"] == "CreateAccountFailure"
        assert data["failureReason"] == "ACCOUNT_EXISTS"
        assert data.get("validationErrors") is None

        async with self.db_session.begin() as session:
            count = await self.count(session, AccountOrm)
            assert count == 1

        assert ACCESS_TOKEN_COOKIE_NAME not in response.cookies
        assert REFRESH_TOKEN_COOKIE_NAME not in response.cookies
        assert self.get_mock("SendGridAPIClient.send").call_count == 0
        assert self.get_mock("segment.analytics.identify").call_count == 0
        assert self.get_mock("segment.analytics.track").call_count == 0
