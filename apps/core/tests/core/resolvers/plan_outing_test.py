import random

from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm
from eave.core.orm.search_region import SearchRegionOrm

from ..base import BaseTestCase

day_seconds = 60 * 60 * 24


class TestPlanOutingEndpoints(BaseTestCase):
    async def test_plan_outing_anonymous(self) -> None:
        response = await self.make_graphql_request(
            "planOuting",
            {
                "input": {
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

    async def test_plan_outing_with_empty_preferences_given(self) -> None:
        response = await self.make_graphql_request(
            "planOuting",
            {
                "input": {
                    "startTime": f"{self.anydatetime(offset=2 * day_seconds).isoformat()}",
                    "searchAreaIds": [s.id.hex for s in random.choices(SearchRegionOrm.all(), k=3)],
                    "budget": "INEXPENSIVE",
                    "headcount": 2,
                    "groupPreferences": [],
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
            account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "planOuting",
            {
                "input": {
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

        data = result.data["planOuting"]
        assert data["outing"]["id"] is not None

    async def test_plan_outing_travel(self) -> None:
        self.mock_compute_routes_response.routes[0].duration.seconds = self.anyint("drive seconds")
        async with self.db_session.begin() as db_session:
            account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "planOuting",
            {
                "input": {
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

        data = result.data["planOuting"]
        assert data["outing"]["travel"]["durationMinutes"] == round(self.anyint("drive seconds") / 60)
