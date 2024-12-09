import random

from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget

from ..base import BaseTestCase

day_seconds = 60 * 60 * 24


class TestPlanOutingEndpoints(BaseTestCase):
    async def test_plan_outing_anonymous(self) -> None:
        vis_id = self.anyuuid()

        response = await self.make_graphql_request(
            "planOutingAnonymous",
            {
                "input": {
                    "visitorId": f"{vis_id}",
                    "startTime": f"{self.anydatetime(offset=2 * day_seconds).isoformat()}",
                    "searchAreaIds": [s.id.hex for s in random.choices(SearchRegionOrm.all(), k=3)],
                    "budget": "INEXPENSIVE",
                    "headcount": 2,
                    "groupPreferences": [
                        {
                            "restaurantCategoryIds": [str(RestaurantCategoryOrm.all()[0].id)],
                            "activityCategoryIds": [str(ActivityCategoryOrm.all()[0].id)],
                        },
                    ],
                },
            },
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["planOuting"]
        assert data["outing"]["id"] is not None

    async def test_plan_outing_authenticated(self) -> None:
        async with self.db_session.begin() as db_session:
            account = await self.make_account(db_session)

        vis_id = self.anyuuid()

        response = await self.make_graphql_request(
            "planOutingAuthenticated",
            {
                "input": {
                    "visitorId": f"{vis_id}",
                    "startTime": f"{self.anydatetime(offset=2 * day_seconds).isoformat()}",
                    "searchAreaIds": [s.id.hex for s in random.choices(SearchRegionOrm.all(), k=3)],
                    "budget": "INEXPENSIVE",
                    "headcount": 2,
                    "groupPreferences": [
                        {
                            "restaurantCategoryIds": [str(RestaurantCategoryOrm.all()[0].id)],
                            "activityCategoryIds": [str(ActivityCategoryOrm.all()[0].id)],
                        }
                    ],
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["planOuting"]
        assert data["outing"]["id"] is not None

    async def test_replan_authenticated(self) -> None:
        async with self.db_session.begin() as sess:
            account = await self.make_account(sess)

            survey = await SurveyOrm.build(
                visitor_id=self.anyuuid(),
                start_time_utc=self.anydatetime(offset=2 * day_seconds),
                timezone=self.anytimezone(),
                search_area_ids=[s.id for s in random.choices(SearchRegionOrm.all(), k=3)],
                budget=OutingBudget.INEXPENSIVE,
                headcount=1,
                account_id=account.id,
            ).save(sess)
            outing = await OutingOrm.build(
                visitor_id=survey.visitor_id,
                survey_id=survey.id,
                account_id=survey.account_id,
            ).save(sess)

        response = await self.make_graphql_request(
            "replanOutingAuthenticated",
            {
                "input": {
                    "outingId": f"{outing.id}",
                    "visitorId": f"{self.anyuuid()}",
                    "groupPreferences": [
                        {
                            "restaurantCategoryIds": [str(RestaurantCategoryOrm.all()[0].id)],
                            "activityCategoryIds": [str(ActivityCategoryOrm.all()[0].id)],
                        }
                    ],
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["replanOuting"]
        assert data["outing"]["id"] is not None

    async def test_replan_anonymous(self) -> None:
        async with self.db_session.begin() as sess:
            survey = await SurveyOrm.build(
                visitor_id=self.anyuuid(),
                start_time_utc=self.anydatetime(offset=2 * day_seconds),
                timezone=self.anytimezone(),
                search_area_ids=[s.id for s in random.choices(SearchRegionOrm.all(), k=3)],
                budget=OutingBudget.INEXPENSIVE,
                headcount=1,
            ).save(sess)
            outing = await OutingOrm.build(
                visitor_id=survey.visitor_id,
                survey_id=survey.id,
                account_id=survey.account_id,
            ).save(sess)

        response = await self.make_graphql_request(
            "replanOutingAnonymous",
            {
                "input": {
                    "outingId": f"{outing.id}",
                    "visitorId": f"{self.anyuuid()}",
                    "groupPreferences": [
                        {
                            "restaurantCategoryIds": [str(RestaurantCategoryOrm.all()[0].id)],
                            "activityCategoryIds": [str(ActivityCategoryOrm.all()[0].id)],
                        }
                    ],
                },
            },
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["replanOuting"]
        assert data["outing"]["id"] is not None

    async def test_replan_anonymous_bad_outing_id(self) -> None:
        # try to replan an outing that doesn't exist
        response = await self.make_graphql_request(
            "replanOutingAnonymous",
            {
                "input": {
                    "outingId": f"{self.anyuuid()}",
                    "visitorId": f"{self.anyuuid()}",
                    "groupPreferences": [
                        {
                            "restaurantCategoryIds": [str(RestaurantCategoryOrm.all()[0].id)],
                            "activityCategoryIds": [str(ActivityCategoryOrm.all()[0].id)],
                        }
                    ],
                },
            },
        )

        result = self.parse_graphql_response(response)

        assert result.data is None
