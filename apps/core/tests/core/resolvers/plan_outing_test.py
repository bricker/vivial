from http import HTTPStatus

from eave.core.orm.outing import OutingOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget

from ..base import BaseTestCase

day_seconds = 60 * 60 * 24


class TestOutingEndpoints(BaseTestCase):
    async def test_plan_outing(self) -> None:
        vis_id = self.anyuuid()

        response = await self.make_graphql_request(
            "planOuting",
            {
                "input": {
                    "visitorId": f"{vis_id}",
                    "startTime": f"{self.anydatetime(offset=2 * day_seconds).isoformat()}",
                    "searchAreaIds": [f"{self.anyuuid()}"],
                    "budget": "INEXPENSIVE",
                    "headcount": 2,
                },
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
                budget=OutingBudget.INEXPENSIVE,
                headcount=1,
            ).save(sess)
            outing = await OutingOrm.build(
                visitor_id=survey.visitor_id,
                survey_id=survey.id,
                account_id=survey.account_id,
            ).save(sess)

        response = await self.make_graphql_request(
            "replanOuting",
            {
                "input": {
                    "outingId": f"{outing.id}",
                    "visitorId": f"{self.anyuuid()}",
                },
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json().get("data").get("replanOuting").get("outing").get("id") is not None

    async def test_replan_bad_outing_id(self) -> None:
        # try to replan an outing that doesn't exist
        response = await self.make_graphql_request(
            "replanOuting",
            {
                "input": {
                    "outingId": f"{self.anyuuid()}",
                    "visitorId": f"{self.anyuuid()}",
                },
            },
        )

        # bcus gql eats error codes
        assert response.status_code == HTTPStatus.OK

        body = response.json()
        assert body.get("data") is None
        assert body.get("errors") is not None and len(body.get("errors")) == 1
        assert body.get("errors")[0].get("message") == "No row was found when one was required"
