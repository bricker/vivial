from eave.core.orm.account import AccountOrm

from ..base import BaseTestCase


class TestUpdateAccountResolver(BaseTestCase):
    async def test_update_account_resolver_with_all_fields_updated(self) -> None:
        async with self.db_session.begin() as db_session:
            original_account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "updateAccount",
            {
                "input": {
                    "email": self.anyemail("email"),
                    "plaintextPassword": self.anystr("plaintext_password"),
                }
            },
            account_id=original_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateAccount"]

        assert data["account"]["id"] == str(original_account.id)
        assert data["account"]["email"] == self.getemail("email")

        async with self.db_session.begin() as db_session:
            updated_account = await AccountOrm.get_one(db_session, original_account.id)
            assert updated_account.email == self.getemail("email")
            assert (
                updated_account.email != original_account.email
            )  # this is just for comprehension, not really a necessary assertion
            assert updated_account.password_key != original_account.password_key
            assert updated_account.password_key_salt != original_account.password_key_salt

            # a passing check that we didn't accidentally write the plain password to the database
            assert updated_account.password_key != self.getstr("plaintext_password")

    async def test_update_account_resolver_with_no_fields_updated(self) -> None:
        async with self.db_session.begin() as db_session:
            original_account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "updateAccount",
            {"input": {}},
            account_id=original_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateAccount"]

        assert data["account"]["id"] == str(original_account.id)
        assert data["account"]["email"] == original_account.email

        async with self.db_session.begin() as db_session:
            updated_account = await AccountOrm.get_one(db_session, original_account.id)
            assert updated_account.email == original_account.email
            assert updated_account.password_key == original_account.password_key
            assert updated_account.password_key_salt == original_account.password_key_salt

    async def test_update_account_resolver_with_null_inputs(self) -> None:
        async with self.db_session.begin() as db_session:
            original_account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "updateAccount",
            {
                "input": {
                    "email": None,
                    "plaintextPassword": None,
                }
            },
            account_id=original_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateAccount"]

        assert data["account"]["id"] == str(original_account.id)
        assert data["account"]["email"] == original_account.email

        async with self.db_session.begin() as db_session:
            updated_account = await AccountOrm.get_one(db_session, original_account.id)
            assert updated_account.email == original_account.email
            assert updated_account.password_key == original_account.password_key
            assert updated_account.password_key_salt == original_account.password_key_salt

    async def test_update_account_resolver_with_only_email_updated(self) -> None:
        async with self.db_session.begin() as db_session:
            original_account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "updateAccount",
            {
                "input": {
                    "email": self.anyemail("email"),
                }
            },
            account_id=original_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateAccount"]

        assert data["account"]["id"] == str(original_account.id)
        assert data["account"]["email"] == self.getemail("email")

        async with self.db_session.begin() as db_session:
            updated_account = await AccountOrm.get_one(db_session, original_account.id)
            assert updated_account.email == self.getemail("email")
            assert updated_account.email != original_account.email
            assert updated_account.password_key == original_account.password_key
            assert updated_account.password_key_salt == original_account.password_key_salt

    async def test_update_account_resolver_with_only_password_updated(self) -> None:
        async with self.db_session.begin() as db_session:
            original_account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "updateAccount",
            {"input": {"plaintextPassword": self.anystr("plaintext_password")}},
            account_id=original_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateAccount"]

        assert data["account"]["id"] == str(original_account.id)
        assert data["account"]["email"] == original_account.email

        async with self.db_session.begin() as db_session:
            updated_account = await AccountOrm.get_one(db_session, original_account.id)
            assert updated_account.email == original_account.email
            assert updated_account.password_key != original_account.password_key
            assert updated_account.password_key_salt != original_account.password_key_salt

            # a passing check that we didn't accidentally write the plain password to the database
            assert updated_account.password_key != self.getstr("plaintext_password")

    async def test_update_account_resolver_with_invalid_password(self) -> None:
        async with self.db_session.begin() as db_session:
            original_account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "updateAccount",
            {
                "input": {
                    "plaintextPassword": self.anyalpha("weak password"),
                }
            },
            account_id=original_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateAccount"]
        assert "account" not in data

        assert data["failureReason"] == "WEAK_PASSWORD"

        async with self.db_session.begin() as db_session:
            updated_account = await AccountOrm.get_one(db_session, original_account.id)
            assert updated_account.email == original_account.email
            assert updated_account.password_key == original_account.password_key
            assert updated_account.password_key_salt == original_account.password_key_salt

            # a passing check that we didn't accidentally write the plain password to the database
            assert updated_account.password_key != self.getalpha("weak password")

    async def test_update_account_resolver_with_invalid_email(self) -> None:
        async with self.db_session.begin() as db_session:
            original_account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "updateAccount",
            {
                "input": {
                    "email": self.anystr("invalid email"),
                }
            },
            account_id=original_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateAccount"]
        assert "account" not in data

        assert data["failureReason"] == "VALIDATION_ERRORS"
        assert len(data["validationErrors"]) == 1
        assert data["validationErrors"][0]["field"] == "email"

        async with self.db_session.begin() as db_session:
            updated_account = await AccountOrm.get_one(db_session, original_account.id)
            assert updated_account.email == original_account.email
            assert updated_account.password_key == original_account.password_key
            assert updated_account.password_key_salt == original_account.password_key_salt

    async def test_update_account_resolver_with_multiple_invalid_inputs(self) -> None:
        async with self.db_session.begin() as db_session:
            original_account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "updateAccount",
            {
                "input": {
                    "email": self.anystr("invalid email"),
                    "plaintextPassword": self.anyalpha("weak password"),
                }
            },
            account_id=original_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateAccount"]
        assert "account" not in data

        # This is an odd case, where the WEAK_PASSWORD is checked before the model is validated, so we should
        # actually only get the WEAK_PASSWORD error back.
        assert data["failureReason"] == "WEAK_PASSWORD"
        assert data["validationErrors"] is None

        async with self.db_session.begin() as db_session:
            updated_account = await AccountOrm.get_one(db_session, original_account.id)
            assert updated_account.email == original_account.email
            assert updated_account.password_key == original_account.password_key
            assert updated_account.password_key_salt == original_account.password_key_salt

    async def test_update_account_resolver_unauthenticated(self) -> None:
        response = await self.make_graphql_request(
            "updateAccount",
            {
                "input": {
                    "email": self.anyemail("email"),
                    "plaintextPassword": self.anystr("plaintext_password"),
                }
            },
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]
        assert "updateAccount" not in data
        assert data["authFailureReason"] == "ACCESS_TOKEN_INVALID"
