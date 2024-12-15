import datetime
from uuid import UUID

from eave.core.orm.outing import OutingOrm

from ..base import BaseTestCase


class TestOutingResolver(BaseTestCase):
    async def test_get_outing_with_2_headcount(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            survey.headcount = 2
            outing = self.make_outing(session, account, survey)

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

        assert data["activity"]["sourceId"] == fetched_outing.activities[0].source_id
        assert data["restaurant"]["sourceId"] == fetched_outing.reservations[0].source_id

        expected_total_cost = (
            self.getint("eventbrite.TicketClass.0.cost.value")
            + self.getint("eventbrite.TicketClass.0.fee.value")
            + self.getint("eventbrite.TicketClass.0.tax.value")
        ) * 2

        assert data["costBreakdown"]["totalCostCents"] == expected_total_cost

    async def test_get_outing_with_1_headcount(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            survey.headcount = 1
            outing = self.make_outing(session, account, survey)

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

        assert data["activity"]["sourceId"] == fetched_outing.activities[0].source_id
        assert data["restaurant"]["sourceId"] == fetched_outing.reservations[0].source_id

        expected_total_cost = (
            self.getint("eventbrite.TicketClass.0.cost.value")
            + self.getint("eventbrite.TicketClass.0.fee.value")
            + self.getint("eventbrite.TicketClass.0.tax.value")
        ) * 1

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

        # We need to do this for typechecking. I'd rather do this than do typeignore
        assert "cost" in self.mock_eventbrite_ticket_class_batch[0]
        assert self.mock_eventbrite_ticket_class_batch[0]["cost"]
        assert "fee" in self.mock_eventbrite_ticket_class_batch[0]
        assert self.mock_eventbrite_ticket_class_batch[0]["fee"]
        assert "tax" in self.mock_eventbrite_ticket_class_batch[0]
        assert self.mock_eventbrite_ticket_class_batch[0]["tax"]

        self.mock_eventbrite_ticket_class_batch[0]["cost"]["value"] = 0
        self.mock_eventbrite_ticket_class_batch[0]["fee"]["value"] = 0
        self.mock_eventbrite_ticket_class_batch[0]["tax"]["value"] = 0

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
