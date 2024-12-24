import datetime
from uuid import UUID

from eave.core.orm.outing import OutingOrm
from eave.core.shared.enums import OutingBudget

from ..base import BaseTestCase


class TestOutingResolver(BaseTestCase):
    async def test_get_outing_with_2_headcount(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            survey.headcount = 2
            outing = self.make_outing(session, account, survey)

        self.set_mock_eventbrite_ticket_class_batch(max_cost_cents=survey.budget.upper_limit_cents)

        response = await self.make_graphql_request(
            "getOuting",
            {
                "input": {
                    "id": str(outing.id),
                },
            },
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["outing"]

        async with self.db_session.begin() as session:
            fetched_outing = await OutingOrm.get_one(session, UUID(data["id"]))

        assert data["activityPlan"]["activity"]["sourceId"] == fetched_outing.activities[0].source_id
        assert data["reservation"]["restaurant"]["sourceId"] == fetched_outing.reservations[0].source_id

        expected_total_cost = self.get_mock_eventbrite_ticket_class_batch_cost() * 2

        assert data["costBreakdown"]["totalCostCents"] == expected_total_cost

    async def test_get_outing_with_1_headcount(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            survey.headcount = 1
            outing = self.make_outing(session, account, survey)

        self.set_mock_eventbrite_ticket_class_batch(max_cost_cents=survey.budget.upper_limit_cents)

        response = await self.make_graphql_request(
            "getOuting",
            {
                "input": {
                    "id": str(outing.id),
                },
            },
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["outing"]

        async with self.db_session.begin() as session:
            fetched_outing = await OutingOrm.get_one(session, UUID(data["id"]))

        assert data["activityPlan"]["activity"]["sourceId"] == fetched_outing.activities[0].source_id
        assert data["reservation"]["restaurant"]["sourceId"] == fetched_outing.reservations[0].source_id

        expected_total_cost = self.get_mock_eventbrite_ticket_class_batch_cost() * 1

        assert data["costBreakdown"]["totalCostCents"] == expected_total_cost

    async def test_get_outing_expired_link(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            outing.activities[0].start_time_utc = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=12)

        response = await self.make_graphql_request(
            "getOuting",
            {
                "input": {
                    "id": str(outing.id),
                },
            },
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["outing"]
        assert data is None

    async def test_get_outing_free(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)

        self.set_mock_eventbrite_ticket_class_batch(max_cost_cents=0)

        response = await self.make_graphql_request(
            "getOuting",
            {
                "input": {
                    "id": str(outing.id),
                },
            },
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["outing"]
        assert data["costBreakdown"]["baseCostCents"] == 0
        assert data["costBreakdown"]["feeCents"] == 0
        assert data["costBreakdown"]["taxCents"] == 0
        assert data["costBreakdown"]["totalCostCents"] == 0
