from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget

from ..base import BaseTestCase


class TestBookingEndpoints(BaseTestCase):
    async def test_valid_create_booking(self) -> None:
        async with self.db_session.begin() as session:
            account = AccountOrm(email=self.anyemail(), plaintext_password=self.anystr())
            session.add(account)

            survey = SurveyOrm(
                account=account,
                visitor_id=self.anyuuid(),
                start_time_utc=self.anydatetime(offset=2 * 60 * 60 * 24),
                timezone=self.anytimezone(),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1, max=2),
            )
            session.add(survey)

            outing = OutingOrm(
                visitor_id=self.anyuuid(),
                account=account,
                survey=survey,
            )
            session.add(outing)

            reserver_details = ReserverDetailsOrm(
                account=account,
                first_name=self.anystr(),
                last_name=self.anystr(),
                phone_number=self.anyphonenumber(),
            )
            session.add(reserver_details)

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        details = result.data["viewer"]["createBooking"]["booking"]
        assert details.get("id") is not None

    async def test_create_booking_from_expired_outing_fails(self) -> None:
        async with self.db_session.begin() as session:
            account = AccountOrm(email=self.anyemail(), plaintext_password=self.anystr())
            session.add(account)

            survey = SurveyOrm(
                account=account,
                visitor_id=self.anyuuid(),
                start_time_utc=self.anydatetime(past=True),
                timezone=self.anytimezone(),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1, max=2),
            )
            session.add(survey)

            outing = OutingOrm(
                visitor_id=self.anyuuid(),
                account=account,
                survey=survey,
            )
            session.add(outing)

            reserver_details = ReserverDetailsOrm(
                account=account,
                first_name=self.anystr(),
                last_name=self.anystr(),
                phone_number=self.anyphonenumber(),
            )
            session.add(reserver_details)

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert "booking" not in data
        assert data["failureReason"] == "START_TIME_TOO_SOON"
