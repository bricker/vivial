from datetime import datetime
from http import HTTPStatus

from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.survey import SurveyOrm
from eave.core.outing.models.search_region_code import SearchRegionCode

from .base import BaseTestCase


class TestOutingEndpoints(BaseTestCase):
    async def test_survey_submit(self) -> None:
        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    submitSurvey(visitorId: "{self.anyuuid()}", startTime: "2024-10-16T21:14:41", searchAreaIds: ["us_ca_la"], budget: 1, headcount: 2) {{
        ... on SurveySubmitSuccess {{
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
        assert response.json().get("data").get("submitSurvey").get("outing").get("id") is not None

    async def test_survey_submit_start_time_with_tz_info(self) -> None:
        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    submitSurvey(visitorId: "{self.anyuuid()}", startTime: "2024-10-18T20:06:48.956Z", searchAreaIds: ["us_ca_la"], budget: 1, headcount: 2) {{
        ... on SurveySubmitSuccess {{
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
        assert response.json().get("data").get("submitSurvey").get("outing").get("id") is not None

    async def test_replan(self) -> None:
        async with self.db_session.begin() as sess:
            survey = await SurveyOrm.create(
                session=sess,
                visitor_id=self.anyuuid(),
                start_time=datetime.now(),
                search_area_ids=[SearchRegionCode.US_CA_LA],
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
    replanOuting(outingId: "{outing.id}") {{
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

    async def test_replan_bad_param_fails(self) -> None:
        # try to replan an outing that doesn't exist
        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": """
mutation {
    replanOuting(outingId: "d27a86dd-f894-4024-9b6c-cdc66fc2f419") {
        ... on ReplanOutingSuccess {
            outing {
                id
            }
        }
    }
}
"""
            },
        )
        # bcus gql eats error codes
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body.get("data") is None
        assert body.get("errors") is not None and len(body.get("errors")) == 1
        assert body.get("errors")[0].get("message") == "No row was found when one was required"
