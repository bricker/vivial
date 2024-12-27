import random

from google.maps.places import PriceLevel
from google.maps.routing import ComputeRoutesResponse, Route
from google.protobuf.duration_pb2 import Duration

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
        self.mock_compute_routes_response = ComputeRoutesResponse(
            routes=[
                Route(
                    duration=Duration(
                        seconds=self.anyint("drive seconds"),
                    ),
                ),
            ],
        )

        self.mock_google_place.price_level = PriceLevel.PRICE_LEVEL_MODERATE

        async with self.db_session.begin() as db_session:
            account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "planOuting",
            {
                "input": {
                    "startTime": f"{self.anydatetime(offset=2 * day_seconds).isoformat()}",
                    "searchAreaIds": [s.id.hex for s in random.choices(SearchRegionOrm.all(), k=3)],
                    "budget": "EXPENSIVE",
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

    async def test_plan_outing_travel_error(self) -> None:
        def _fakeraise() -> None:
            raise Exception("fake error")

        self.get_mock("google routes compute_routes").side_effect = _fakeraise

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
        assert data["outing"]["travel"] is None
