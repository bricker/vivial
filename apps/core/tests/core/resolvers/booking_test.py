from http import HTTPStatus

from eave.core.graphql.types.booking import CreateBookingErrorCode
from eave.core.graphql.types.search_region import SearchRegionCode
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.reserver_details import ReserverDetailsOrm
from eave.core.internal.orm.survey import SurveyOrm

from ..base import BaseTestCase


class TestBookingEndpoints(BaseTestCase):
    async def test_valid_create_booking(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session=session)
            outing = await self.make_outing(session=session, account_id=account.id)
            reserver_details = await ReserverDetailsOrm.create(
                session=session,
                account_id=account.id,
                first_name=self.anystr(),
                last_name=self.anystr(),
                phone_number="1234567890",
            )

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    createBooking(input: {{
        accountId: "{account.id}", outingId: "{outing.id}", reserverDetailsId: "{reserver_details.id}"
    }}) {{
        ... on CreateBookingSuccess {{
            booking {{
                id
            }}
        }}
        ... on CreateBookingError {{
            errorCode
        }}
    }}
}}
"""
            },
        )
        assert response.status_code == HTTPStatus.OK
        details = response.json().get("data").get("createBooking").get("booking")
        assert details.get("id") is not None

    async def test_create_booking_from_expired_outing_fails(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session=session)
            # cant use `create` convenience method since that includes validation
            survey = SurveyOrm(
                visitor_id=self.anyuuid(),
                # survey time is expired
                start_time=self.anydatetime(past=True).replace(tzinfo=None),
                search_area_ids=[SearchRegionCode.US_CA_LA1],
                budget=self.anyint(min=0, max=3),
                headcount=self.anyint(min=1, max=2),
            )
            session.add(survey)
            await session.flush()
            outing = await OutingOrm.create(
                session=session,
                visitor_id=self.anyuuid(),
                account_id=account.id,
                survey_id=survey.id,
            )
            reserver_details = await ReserverDetailsOrm.create(
                session=session,
                account_id=account.id,
                first_name=self.anystr(),
                last_name=self.anystr(),
                phone_number="1234567890",
            )

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    createBooking(input: {{
        accountId: "{account.id}", outingId: "{outing.id}", reserverDetailsId: "{reserver_details.id}"
    }}) {{
        ... on CreateBookingSuccess {{
            booking {{
                id
            }}
        }}
        ... on CreateBookingError {{
            errorCode
        }}
    }}
}}
"""
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json().get("data").get("createBooking").get("booking") is None
        assert (
            response.json().get("data").get("createBooking").get("errorCode")
            == CreateBookingErrorCode.START_TIME_TOO_SOON
        )
