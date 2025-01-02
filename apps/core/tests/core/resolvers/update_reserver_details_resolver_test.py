from eave.core.orm.account import AccountOrm
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.outing_preferences import OutingPreferencesOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm

from ..base import BaseTestCase


class TestUpdateReserverDetails(BaseTestCase):
    async def test_update_reserver_details(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            reserver_details = self.make_reserver_details(session, account)

        response = await self.make_graphql_request(
            "updateReserverDetails",
            {
                "input": {
                    "id": str(reserver_details.id),
                    "firstName": self.anystr("firstName"),
                    "lastName": self.anystr("lastName"),
                    "phoneNumber": self.anyphonenumber("phoneNumber"),
                }
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateReserverDetails"]
        assert data["__typename"] == "UpdateReserverDetailsSuccess"
        assert data["reserverDetails"]["id"] == str(reserver_details.id)
        assert data["reserverDetails"]["firstName"] == self.getstr("firstName")
        assert data["reserverDetails"]["lastName"] == self.getstr("lastName")
        assert data["reserverDetails"]["phoneNumber"] == self.getphonenumber("phoneNumber")

        async with self.db_session.begin() as session:
            reserver_details_fetched = await ReserverDetailsOrm.get_one(session, account_id=account.id, uid=reserver_details.id)

        assert reserver_details_fetched.first_name == self.getstr("firstName")
        assert reserver_details_fetched.last_name == self.getstr("lastName")
        assert reserver_details_fetched.phone_number == self.getstr("phoneNumber")

    async def test_update_reserver_details_partial(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            reserver_details = self.make_reserver_details(session, account)

        response = await self.make_graphql_request(
            "updateReserverDetails",
            {
                "input": {
                    "id": str(reserver_details.id),
                    "phoneNumber": self.anyphonenumber("phoneNumber"),
                }
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateReserverDetails"]
        assert data["__typename"] == "UpdateReserverDetailsSuccess"
        assert data["reserverDetails"]["id"] == str(reserver_details.id)
        assert data["reserverDetails"]["firstName"] == reserver_details.first_name
        assert data["reserverDetails"]["lastName"] == reserver_details.last_name
        assert data["reserverDetails"]["phoneNumber"] == self.getphonenumber("phoneNumber")

        async with self.db_session.begin() as session:
            reserver_details_fetched = await ReserverDetailsOrm.get_one(session, account_id=account.id, uid=reserver_details.id)

        assert reserver_details_fetched.first_name == reserver_details.first_name
        assert reserver_details_fetched.last_name == reserver_details.last_name
        assert reserver_details_fetched.phone_number == self.getstr("phoneNumber")

    async def test_update_reserver_details_unauthenticated(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            reserver_details = self.make_reserver_details(session, account)
            other_account = self.make_account(session)

        response = await self.make_graphql_request(
            "updateReserverDetails",
            {
                "input": {
                    "id": str(reserver_details.id),
                    "firstName": self.anystr("firstName"),
                    "lastName": self.anystr("lastName"),
                    "phoneNumber": self.anystr("phoneNumber"),
                }
            },
            account_id=other_account.id,
        )

        result = self.parse_graphql_response(response)
        assert not result.data
        assert result.errors # The reserver details should not be found in the database, and throw an error

        async with self.db_session.begin() as session:
            reserver_details_fetched = await ReserverDetailsOrm.get_one(session, account_id=account.id, uid=reserver_details.id)

        assert reserver_details_fetched.first_name == reserver_details.first_name
        assert reserver_details_fetched.last_name == reserver_details.last_name
        assert reserver_details_fetched.phone_number == reserver_details.phone_number
