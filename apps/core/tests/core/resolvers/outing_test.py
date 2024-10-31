from http import HTTPStatus
import unittest.mock

from eave.stdlib.eventbrite.models.event import Event

from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.survey import SurveyOrm
from eave.core.outing.models.search_region_code import SearchRegionCode

from ..base import BaseTestCase

day_seconds = 60 * 60 * 24


class TestOutingEndpoints(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.patch(
            name="eventbrite get_event_by_id",
            patch=unittest.mock.patch("eave.stdlib.eventbrite.client.EventbriteClient.get_event_by_id"),
            return_value=Event(),
        )
        self.patch(
            name="eventbrite get_event_description",
            patch=unittest.mock.patch("eave.stdlib.eventbrite.client.EventbriteClient.get_event_description"),
            return_value="description",
        )
        self.patch(
            name="google places searchNearby",
            patch=unittest.mock.patch("eave.stdlib.google.places.client.GooglePlacesClient.search_nearby"),
            return_value=[],
        )

    async def test_survey_submit(self) -> None:
        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    submitSurvey(visitorId: "{self.anyuuid()}",
        startTime: "{self.anydatetime(offset=2 * day_seconds).isoformat()}",
        searchAreaIds: ["us_ca_la_1"],
        budget: 1,
        headcount: 2) {{
        ... on SurveySubmitSuccess {{
            outing {{
                id
            }}
        }}
        ... on SurveySubmitError {{
            errorCode
        }}
    }}
}}
"""
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json().get("data").get("submitSurvey").get("outing").get("id") is not None

    async def test_replan(self) -> None:
        async with self.db_session.begin() as sess:
            survey = await SurveyOrm.create(
                session=sess,
                visitor_id=self.anyuuid(),
                start_time=self.anydatetime(offset=2 * day_seconds),
                search_area_ids=[SearchRegionCode.US_CA_LA1],
                budget=1,
                headcount=1,
            )
            outing = await OutingOrm.create(
                session=sess,
                visitor_id=survey.visitor_id,
                survey_id=survey.id,
                account_id=survey.account_id,
            )

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    replanOuting(outingId: "{outing.id}", visitorId: "{self.anyuuid()}") {{
        ... on ReplanOutingSuccess {{
            outing {{
                id
            }}
        }}
    }}
}}
"""
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json().get("data").get("replanOuting").get("outing").get("id") is not None

    async def test_replan_bad_outing_id(self) -> None:
        # try to replan an outing that doesn't exist
        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    replanOuting(outingId: "{self.anyuuid()}", visitorId: "{self.anyuuid()}") {{
        ... on ReplanOutingSuccess {{
            outing {{
                id
            }}
        }}
    }}
}}
"""
            },
        )
        # bcus gql eats error codes
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body.get("data") is None
        assert body.get("errors") is not None and len(body.get("errors")) == 1
        assert body.get("errors")[0].get("message") == "No row was found when one was required"
