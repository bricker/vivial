import unittest.mock
from http import HTTPStatus
from google.maps.places_v1.types import Place
from eave.core.orm.outing import OutingOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from ..base import BaseTestCase

day_seconds = 60 * 60 * 24


class MockPlacesResponse:
    places: list[Place]

    def __init__(self, places: list[Place]):
        self.places = places


class TestOutingEndpoints(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.patch(
            name="eventbrite get_event_by_id",
            patch=unittest.mock.patch("eave.stdlib.eventbrite.client.EventbriteClient.get_event_by_id"),
            return_value={},
        )
        self.patch(
            name="eventbrite get_event_description",
            patch=unittest.mock.patch("eave.stdlib.eventbrite.client.EventbriteClient.get_event_description"),
            return_value="description",
        )
        self.patch(
            name="google places searchNearby",
            patch=unittest.mock.patch(
                "google.maps.places_v1.services.places.async_client.PlacesAsyncClient.search_nearby"
            ),
            return_value=MockPlacesResponse([]),
        )

    async def test_plan_outing(self) -> None:
        vis_id = self.anyuuid()

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    planOuting(input: {{
        visitorId: "{vis_id}",
        startTime: "{self.anydatetime(offset=2 * day_seconds).isoformat()}",
        searchAreaIds: ["{self.anyuuid()}"],
        budget: ONE,
        headcount: 2,
        group: [
            {{
                visitorId: "{vis_id}",
            }},
        ]
    }}) {{
        ... on PlanOutingSuccess {{
            outing {{
                id
            }}
        }}
        ... on PlanOutingError {{
            errorCode
        }}
    }}
}}
"""
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json().get("data").get("planOuting").get("outing").get("id") is not None

    async def test_replan(self) -> None:
        async with self.db_session.begin() as sess:
            survey = await SurveyOrm.build(
                visitor_id=self.anyuuid(),
                start_time=self.anydatetime(offset=2 * day_seconds),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=1,
                headcount=1,
            ).save(session=sess)
            outing = await OutingOrm.build(
                visitor_id=survey.visitor_id,
                survey_id=survey.id,
                account_id=survey.account_id,
            ).save(session=sess)

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    replanOuting(input: {{
        outingId: "{outing.id}", visitorId: "{self.anyuuid()}"
    }}) {{
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
    replanOuting(input: {{
        outingId: "{self.anyuuid()}", visitorId: "{self.anyuuid()}"
    }}) {{
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
