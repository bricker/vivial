from eave.core.orm.account import (
    AccountOrm,
    InvalidPasswordError,
    WeakPasswordError,
    validate_password_strength_or_exception,
)
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.booking import BookingOrm
from eave.core.orm.outing_preferences import OutingPreferencesOrm

from ..base import BaseTestCase


class TestAccountOrm(BaseTestCase):
    async def test_new_account_record(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0
            new_account = AccountOrm(
                session,
                email=self.anyemail("email"),
                plaintext_password=self.anystr("plaintext_password"),
                visitor_id=self.anystr("visitor_id"),
            )

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 1
            fetched_account = await AccountOrm.get_one(session, new_account.id)

            assert fetched_account.email == self.getemail("email")
            assert fetched_account.password_key
            assert fetched_account.password_key != self.getstr("plaintext_password")
            assert fetched_account.visitor_id == self.getstr("visitor_id")

    async def test_account_validation_invalid_email(self) -> None:
        with self.assertRaises(InvalidRecordError):
            async with self.db_session.begin() as session:
                assert await self.count(session, AccountOrm) == 0
                AccountOrm(
                    session,
                    email="invalid email",
                    plaintext_password=self.anystr("plaintext_password"),
                    visitor_id=None,
                )

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0

    async def test_account_validation_weak_password(self) -> None:
        with self.assertRaises(WeakPasswordError):
            async with self.db_session.begin() as session:
                assert await self.count(session, AccountOrm) == 0
                AccountOrm(session, email=self.anyemail(), plaintext_password="weak password", visitor_id=None)

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0

    async def test_account_validation_empty_password(self) -> None:
        with self.assertRaises(WeakPasswordError):
            async with self.db_session.begin() as session:
                assert await self.count(session, AccountOrm) == 0
                AccountOrm(session, email=self.anyemail(), plaintext_password="", visitor_id=None)

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0

    async def test_account_validation_null_password(self) -> None:
        # This is a check to see what happens if `null` is given as the password.
        # Although the typing system won't allow it, at runtime it could happen.
        with self.assertRaises(WeakPasswordError):
            async with self.db_session.begin() as session:
                assert await self.count(session, AccountOrm) == 0
                AccountOrm(
                    session,
                    email=self.anyemail(),
                    plaintext_password=None,  # type:ignore - testing what happens if None happens to be passed in at runtime
                    visitor_id=None,
                )

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0

    async def test_account_verify_password_verified(self) -> None:
        async with self.db_session.begin() as session:
            new_account = AccountOrm(
                session, email=self.anyemail(), plaintext_password=self.anystr("plaintext_password"), visitor_id=None
            )

        async with self.db_session.begin() as session:
            fetched_account = await AccountOrm.get_one(session, new_account.id)

            try:
                assert fetched_account.verify_password_or_exception(
                    plaintext_password=self.getstr("plaintext_password")
                )
            except InvalidPasswordError as e:
                self.fail(e)

    async def test_account_verify_password_not_verified(self) -> None:
        async with self.db_session.begin() as session:
            new_account = AccountOrm(
                session, email=self.anyemail(), plaintext_password=self.anystr("plaintext_password"), visitor_id=None
            )

        async with self.db_session.begin() as session:
            fetched_account = await AccountOrm.get_one(session, new_account.id)

            with self.assertRaises(InvalidPasswordError):
                fetched_account.verify_password_or_exception(
                    plaintext_password=self.anystr("incorrect plaintext_password")
                )

    async def test_account_set_password_with_valid_password(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0
            new_account = AccountOrm(
                session, email=self.anyemail(), plaintext_password=self.anystr("plaintext_password"), visitor_id=None
            )

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 1

            fetched_account = await AccountOrm.get_one(session, new_account.id)
            assert fetched_account.password_key != self.getstr("plaintext_password")

            # Test assumptions before changing password
            assert fetched_account.password_key == new_account.password_key
            assert fetched_account.password_key_salt == new_account.password_key_salt

            fetched_account.set_password(plaintext_password=self.anystr("new plaintext_password"))
            assert fetched_account.password_key != self.getstr("new plaintext_password")
            assert fetched_account.password_key != new_account.password_key
            assert fetched_account.password_key_salt != new_account.password_key_salt

        async with self.db_session.begin() as session:
            next_fetched_account = await AccountOrm.get_one(session, new_account.id)
            assert next_fetched_account.password_key == fetched_account.password_key
            assert next_fetched_account.password_key_salt == fetched_account.password_key_salt

            assert next_fetched_account.password_key != new_account.password_key
            assert next_fetched_account.password_key_salt != new_account.password_key_salt

    async def test_account_set_password_with_weak_password(self) -> None:
        with self.assertRaises(WeakPasswordError):
            async with self.db_session.begin() as session:
                assert await self.count(session, AccountOrm) == 0
                new_account = self.make_account(session)
                new_account.set_password(plaintext_password="weak password")

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0

    async def test_account_set_password_with_empty_password(self) -> None:
        with self.assertRaises(WeakPasswordError):
            async with self.db_session.begin() as session:
                assert await self.count(session, AccountOrm) == 0
                new_account = self.make_account(session)
                new_account.set_password(plaintext_password="")

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0

    async def test_account_set_password_with_null_password(self) -> None:
        # This is a check to see what happens if `null` is given as the password.
        # Although the typing system won't allow it, at runtime it could happen.
        with self.assertRaises(WeakPasswordError):
            async with self.db_session.begin() as session:
                assert await self.count(session, AccountOrm) == 0
                new_account = self.make_account(session)
                new_account.set_password(plaintext_password=None)  # type:ignore - testing what happens if None happens to be passed in at runtime

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0

    async def test_account_password_strength_validation(self) -> None:
        try:
            assert validate_password_strength_or_exception(plaintext_password=self.anystr())
        except WeakPasswordError as e:
            self.fail(e)

        with self.assertRaises(WeakPasswordError):
            validate_password_strength_or_exception(plaintext_password="")

        with self.assertRaises(WeakPasswordError):
            validate_password_strength_or_exception(plaintext_password=None)  # type:ignore - test what happens if null passed in at runtime

        with self.assertRaises(WeakPasswordError):
            # No alpha or special character
            validate_password_strength_or_exception(plaintext_password="0123456789")

        with self.assertRaises(WeakPasswordError):
            # Too short
            validate_password_strength_or_exception(plaintext_password="123aBc!")

        with self.assertRaises(WeakPasswordError):
            # No special characters
            validate_password_strength_or_exception(plaintext_password="1234abcdEFG")

        with self.assertRaises(WeakPasswordError):
            # No alpha
            validate_password_strength_or_exception(plaintext_password="1234!@#$%^&")

        with self.assertRaises(WeakPasswordError):
            # No digits
            validate_password_strength_or_exception(plaintext_password="abcdEFG!@#$%^")

        with self.assertRaises(WeakPasswordError):
            # No digits or alpha
            validate_password_strength_or_exception(plaintext_password="!@#$%*&^%$#$%^")

        with self.assertRaises(WeakPasswordError):
            # No digits or special characters
            validate_password_strength_or_exception(plaintext_password="abcdefghiJKL")

        with self.assertRaises(WeakPasswordError):
            # Too long
            validate_password_strength_or_exception(plaintext_password=self.anyalpha(length=300) + "123!@#")

    async def test_account_associations(self) -> None:
        async with self.db_session.begin() as session:
            account = AccountOrm(
                session, email=self.anyemail(), plaintext_password=self.anystr("plaintext_password"), visitor_id=None
            )
            reserver_details = self.make_reserver_details(session, account)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)

            booking = BookingOrm(
                session,
                accounts=[],
                outing=outing,
                reserver_details=reserver_details,
            )

            account.bookings.append(booking)

            outing_preferences = OutingPreferencesOrm(
                session,
                account=account,
                activity_category_ids=[],
                restaurant_category_ids=[],
            )

        async with self.db_session.begin() as session:
            fetched_account = await AccountOrm.get_one(session, account.id)

            assert len(fetched_account.bookings) == 1
            assert fetched_account.bookings[0].id == booking.id

            assert fetched_account.outing_preferences is not None
            assert fetched_account.outing_preferences.id == outing_preferences.id

            assert len(booking.accounts) == 1
            assert booking.accounts[0].id == fetched_account.id
