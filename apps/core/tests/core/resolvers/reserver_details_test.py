from http import HTTPStatus

from eave.core.graphql.resolvers.mutations.viewer.submit_reserver_details import SubmitReserverDetailsFailureReason
from eave.stdlib.cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME

from ..base import BaseTestCase


class TestReserverDetailsEndpoints(BaseTestCase):
    async def test_valid_reserver_details_form_submit(self) -> None:
        async with self.db_session.begin() as session:
            await self.make_account(session=session)

        phone_num = "+12345678900"

        response = await self.make_graphql_request("createBooking", {
            "input": {
                "firstName": self.anystr("first"),
                "lastName": self.anystr("last"),
                "phoneNumber": phone_num,
            },
        })

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        details = result.data["viewer"]["submitReserverDetails"]["reserverDetails"]
        assert details["id"] is not None
        assert details["firstName"] == self.getstr("first")
        assert details["lastName"] == self.getstr("last")
        assert details["phoneNumber"] == phone_num

    async def test_reserver_details_form_submit_invalid_phone_number(self) -> None:
        async with self.db_session.begin() as session:
            await self.make_account(session=session)

        # invalid phone number
        phone_num = "1-800-BEANS-FOR-BREAKFAST"

        response = await self.make_graphql_request("createBooking", {
            "input": {
                "firstName": self.anystr("first"),
                "lastName": self.anystr("last"),
                "phoneNumber": phone_num,
            },
        })

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["submitReserverDetails"]
        assert "reserverDetails" not in data
        assert data["failureReason"] == "VALIDATION_ERRORS"
        assert len(data["validationErrors"]) == 1
        assert data["validationErrors"][0]["field"] == "phone_number"
