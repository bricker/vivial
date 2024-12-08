from eave.core.lib.geo import GeoPoint
from eave.core.orm.activity import ActivityOrm
from eave.core.shared.address import Address
from eave.core.orm.reserver_details import ReserverDetailsOrm

from ..base import BaseTestCase


class TestReserverDetailsOrm(BaseTestCase):
    async def test_valid_reserver_details_record(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session)

            reserver_details = await ReserverDetailsOrm.build(
                account_id=account.id,
                first_name=self.anyalpha(),
                last_name=self.anyalpha(),
                phone_number="123-456-7890",
            ).save(session)

        assert reserver_details.id is not None

    async def test_reserver_details_validation(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session)

        reserver_details = ReserverDetailsOrm.build(
            account_id=account.id,
            first_name=self.anyalpha("first_name"),
            last_name=self.anyalpha("last_name"),
            phone_number="123-456-7890",
        )

        validation_errors = reserver_details.validate()
        assert len(validation_errors) == 0

        reserver_details.first_name = ""
        validation_errors = reserver_details.validate()
        assert len(validation_errors) == 1
        assert validation_errors[0].field == "first_name"
        reserver_details.first_name = self.getstr("first_name")

        reserver_details.last_name = ""
        validation_errors = reserver_details.validate()
        assert len(validation_errors) == 1
        assert validation_errors[0].field == "last_name"
        reserver_details.last_name = self.getstr("last_name")

        reserver_details.phone_number = "+11234567890"
        assert len(reserver_details.validate()) == 0
        reserver_details.phone_number = "+1 (123)-456-7890"
        assert len(reserver_details.validate()) == 0
        reserver_details.phone_number = "+1(123)-456-7890"
        assert len(reserver_details.validate()) == 0
        reserver_details.phone_number = "(123)-456-7890"
        assert len(reserver_details.validate()) == 0
        reserver_details.phone_number = "(123) 456 7890"
        assert len(reserver_details.validate()) == 0
        reserver_details.phone_number = "(123)456-7890"
        assert len(reserver_details.validate()) == 0
        reserver_details.phone_number = "(123)4567890"
        assert len(reserver_details.validate()) == 0
        reserver_details.phone_number = "1234567890"
        assert len(reserver_details.validate()) == 0
        reserver_details.phone_number = "123-456-7890"
        assert len(reserver_details.validate()) == 0

        reserver_details.phone_number = "123"
        validation_errors = reserver_details.validate()
        assert len(validation_errors) == 1
        assert validation_errors[0].field == "phone_number"

        reserver_details.phone_number = "123_456_7890"
        validation_errors = reserver_details.validate()
        assert len(validation_errors) == 1
        assert validation_errors[0].field == "phone_number"

        reserver_details.phone_number = "abc-123-defg"
        validation_errors = reserver_details.validate()
        assert len(validation_errors) == 1
        assert validation_errors[0].field == "phone_number"

        reserver_details.phone_number = "(12)-345-6789"
        validation_errors = reserver_details.validate()
        assert len(validation_errors) == 1
        assert validation_errors[0].field == "phone_number"

        reserver_details.phone_number = "(123)-45-67890"
        validation_errors = reserver_details.validate()
        assert len(validation_errors) == 1
        assert validation_errors[0].field == "phone_number"
