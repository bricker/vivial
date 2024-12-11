import random

from eave.core.orm.account import AccountOrm
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource

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
                    phone_number=self.anyphonenumber()
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
