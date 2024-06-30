from http import HTTPStatus

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.team import bq_dataset_id
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.core_api.models.virtual_event import (
    BigQueryFieldMode,
    VirtualEventDetailsQueryInput,
    VirtualEventField,
)
from eave.stdlib.core_api.operations.virtual_event import GetMyVirtualEventDetailsRequest, ListMyVirtualEventsRequest

from .base import BaseTestCase

_WORDS = ["abc def", "ghi jkl", "mno pqr", "stu vwx"]


class TestVirtualEventRequests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team1 = await self.make_team(s)
            self._account_team1 = await self.make_account(s, team_id=self._team1.id)

            self._team1_virtual_events = [
                await VirtualEventOrm.create(
                    session=s,
                    team_id=self._team1.id,
                    view_id=self.anyhex(f"view_id {i}"),
                    description=self.anystr(f"description {i}"),
                    readable_name=word,
                )
                for i, word in enumerate(_WORDS)
            ]

            self._team2 = await self.make_team(s)
            self._account_team2 = await self.make_account(s, team_id=self._team2.id)
            self._team2_virtual_events = [
                # Create virtual events for another team to test team scoping.
                # The virtual event properties (view_id etc) are deliberately the same as the other team's virtual events
                # This implicitly tests query isolation
                await VirtualEventOrm.create(
                    session=s,
                    team_id=self._team2.id,
                    view_id=self.gethex(f"view_id {i}"),
                    description=self.getstr(f"description {i}"),
                    readable_name=word,
                )
                for i, word in enumerate(_WORDS)
            ]

            self._team2_virtual_events.append(
                # Create another virtual event only for team2 with different properties
                await VirtualEventOrm.create(
                    session=s,
                    team_id=self._team2.id,
                    view_id=self.anyhex("team2 view_id 99"),
                    description=self.anystr("team2 description 99"),
                    readable_name="yz",
                )
            )

    async def test_get_virtual_events_with_search_term_match(self) -> None:
        response = await self.make_request(
            path=ListMyVirtualEventsRequest.config.path,
            payload=ListMyVirtualEventsRequest.RequestBody(
                query="abc",
            ),
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = ListMyVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 1
        assert response_obj.virtual_events[0].id == self._team1_virtual_events[0].id

    async def test_get_virtual_events_with_search_term_no_match(self) -> None:
        response = await self.make_request(
            path=ListMyVirtualEventsRequest.config.path,
            payload=ListMyVirtualEventsRequest.RequestBody(
                query="yz",
            ),
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = ListMyVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 0

    async def test_get_virtual_events_with_no_search_term(self) -> None:
        """
        If someone from Team 1 requests all virtual events (no query filter), then they should only receive Team 1's events.
        """

        response = await self.make_request(
            path=ListMyVirtualEventsRequest.config.path,
            payload=ListMyVirtualEventsRequest.RequestBody(),
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = ListMyVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == len(_WORDS)
        assert sorted(e.id for e in response_obj.virtual_events) == sorted(e.id for e in self._team1_virtual_events)

    async def test_get_virtual_events_with_search_term_team_scope(self) -> None:
        """
        If someone from Team 1 searches for a virtual event owned by Team 2, then there should be no results.
        If someone from Team 2 searches for that same virtual event, then there should be results.
        """

        response = await self.make_request(
            path=ListMyVirtualEventsRequest.config.path,
            payload=ListMyVirtualEventsRequest.RequestBody(
                query="yz",
            ),
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = ListMyVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 0

        response = await self.make_request(
            path=ListMyVirtualEventsRequest.config.path,
            payload=ListMyVirtualEventsRequest.RequestBody(
                query="yz",
            ),
            account_id=self._account_team2.id,
            access_token=self._account_team2.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = ListMyVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 1
        assert response_obj.virtual_events[0].id == self._team2_virtual_events[-1].id

    async def test_get_virtual_event_details_with_existing_view(self):
        target_vevent = self._team1_virtual_events[0]

        dataset = EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_dataset(dataset_id=bq_dataset_id(self._team1.id))

        bq_view = EAVE_INTERNAL_BIGQUERY_CLIENT.construct_table(
            dataset_id=dataset.dataset_id, table_id=target_vevent.view_id
        )
        bq_view.view_query = f'SELECT STRUCT("{self.anyhex()}" as `{self.anyalpha("field name 1")}`, "{self.anyhex()}" as `{self.anyalpha("field name 2")}`) as `{self.anyalpha("field name 0")}`'

        bq_view = EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_table(table=bq_view, ctx=self.empty_ctx)
        bq_view.schema = (
            SchemaField(
                name=self.getalpha("field name 0"),
                field_type=SqlTypeNames.STRUCT,
                mode=BigQueryFieldMode.NULLABLE,
                description=self.anystr("field description 0"),
                fields=(
                    SchemaField(
                        name=self.getalpha("field name 1"),
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                        description=self.anystr("field description 1"),
                    ),
                    SchemaField(
                        name=self.getalpha("field name 2"),
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                        description=self.anystr("field description 2"),
                    ),
                ),
            ),
        )

        bq_view = EAVE_INTERNAL_BIGQUERY_CLIENT.update_table(table=bq_view, ctx=self.empty_ctx, fields=["schema"])

        response = await self.make_request(
            path=GetMyVirtualEventDetailsRequest.config.path,
            payload=GetMyVirtualEventDetailsRequest.RequestBody(
                virtual_event=VirtualEventDetailsQueryInput(
                    id=target_vevent.id,
                )
            ),
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetMyVirtualEventDetailsRequest.ResponseBody(**response.json())
        assert response_obj.virtual_event.id == target_vevent.id
        assert response_obj.virtual_event.view_id == target_vevent.view_id
        assert response_obj.virtual_event.readable_name == target_vevent.readable_name
        assert response_obj.virtual_event.description == target_vevent.description
        assert response_obj.virtual_event.fields == [
            VirtualEventField(
                name=self.gethex("field name 0"),
                description=self.getstr("field description 0"),
                field_type=SqlTypeNames.STRUCT,
                mode=BigQueryFieldMode.NULLABLE,
                fields=[
                    VirtualEventField(
                        name=self.gethex("field name 1"),
                        description=self.getstr("field description 1"),
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                        fields=None,
                    ),
                    VirtualEventField(
                        name=self.gethex("field name 2"),
                        description=self.getstr("field description 2"),
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                        fields=None,
                    ),
                ],
            ),
        ]

    async def test_get_virtual_event_details_with_missing_view(self):
        target_vevent = self._team1_virtual_events[0]
        response = await self.make_request(
            path=GetMyVirtualEventDetailsRequest.config.path,
            payload=GetMyVirtualEventDetailsRequest.RequestBody(
                virtual_event=VirtualEventDetailsQueryInput(
                    id=target_vevent.id,
                )
            ),
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetMyVirtualEventDetailsRequest.ResponseBody(**response.json())
        assert response_obj.virtual_event.id == target_vevent.id
        assert response_obj.virtual_event.view_id == target_vevent.view_id
        assert response_obj.virtual_event.readable_name == target_vevent.readable_name
        assert response_obj.virtual_event.description == target_vevent.description
        assert response_obj.virtual_event.fields is None
