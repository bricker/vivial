from http import HTTPStatus

from .base import BaseTestCase


class TestSurveyEndpoint(BaseTestCase):
    async def test_survey_submit(self) -> None:
        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": """
mutation {
    submitSurveyForPlan(visitorId: "abc124", startTimeIso: "2024-10-16T21:14:41", searchAreaIds: ["us_ca_la"], budget: 1, headcount: 2) {
        id
    }
}
"""
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json().get("data").get("submitSurveyForPlan").get("id") is not None
