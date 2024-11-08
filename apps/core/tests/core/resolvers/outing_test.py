from http import HTTPStatus

from eave.core.graphql.types.search_region_code import SearchRegionCode
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.survey import SurveyOrm

from ..base import BaseTestCase

day_seconds = 60 * 60 * 24


class TestOutingEndpoints(BaseTestCase):
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
        searchAreaIds: [US_CA_LA1],
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
