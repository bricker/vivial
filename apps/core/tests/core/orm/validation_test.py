from eave.core.orm.account import AccountOrm
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.reserver_details import ReserverDetailsOrm

from ..base import BaseTestCase


class TestValidation(BaseTestCase):
    async def test_global_validation_passes(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0
            assert await self.count(session, ReserverDetailsOrm) == 0

        try:
            async with self.db_session.begin() as session:
                account = AccountOrm(
                    email=self.anyemail(),
                    plaintext_password=self.anystr(),
                )
                session.add(account)

                reserver_details = ReserverDetailsOrm(
                    account=account,
                    first_name=self.anyalpha(),
                    last_name=self.anyalpha(),
                    phone_number=self.anyphonenumber(),
                )
                session.add(reserver_details)
        except InvalidRecordError as e:
            self.fail(e)

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 1
            assert await self.count(session, ReserverDetailsOrm) == 1

    async def test_global_validation_fails(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0
            assert await self.count(session, ReserverDetailsOrm) == 0

        with self.assertRaises(InvalidRecordError):
            async with self.db_session.begin() as session:
                account = AccountOrm(
                    email=self.anyemail(),
                    plaintext_password=self.anystr(),
                )
                session.add(account)

                reserver_details = ReserverDetailsOrm(
                    account=account,
                    first_name="",
                    last_name="",
                    phone_number="",
                )
                session.add(reserver_details)

        async with self.db_session.begin() as session:
            assert await self.count(session, AccountOrm) == 0
            assert await self.count(session, ReserverDetailsOrm) == 0

    async def test_adding_previous_session_object_to_new_session(self) -> None:
        # This isn't really testing validations, it's just something I wanted to test and happened to be in this file.
        async with self.db_session.begin() as session:
            account = AccountOrm(
                email=self.anyemail("old email"),
                plaintext_password=self.anystr(),
            )
            session.add(account)

        async with self.db_session.begin() as session:
            session.add(account)
            account.email = self.anyemail("new email")

        assert account.email == self.getemail("new email")

        async with self.db_session.begin() as session:
            fetched_account = await AccountOrm.get_one(session, account.id)
            assert fetched_account.email == self.getemail("new email")
