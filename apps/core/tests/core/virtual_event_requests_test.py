from http import HTTPStatus

from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.core_api.operations.virtual_event import ListMyVirtualEventsRequest

from .base import BaseTestCase


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
                    view_id=self.anystr(f"view_id {i}"),
                    description=self.anystr(f"description {i}"),
                    readable_name=self.anystr(f"readable_name {i}"),
                )
                for i in range(2)
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
                    view_id=self.getstr(f"view_id {i}"),
                    description=self.getstr(f"description {i}"),
                    readable_name=self.getstr(f"readable_name {i}"),
                )
                for i in range(2)
            ]

            self._team2_virtual_events.append(
                # Create another virtual event only for team2 with different properties
                await VirtualEventOrm.create(
                    session=s,
                    team_id=self._team2.id,
                    view_id=self.anystr("team2 view_id"),
                    description=self.anystr("team2 description"),
                    readable_name=self.anystr("team2 readable_name"),
                )
            )

    async def test_get_virtual_events_with_search_term_match(self) -> None:
        response = await self.make_request(
            path=ListMyVirtualEventsRequest.config.path,
            payload=ListMyVirtualEventsRequest.RequestBody(
                query=self.getstr("readable_name 0"),
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
                query=self.anystr(),
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
        assert len(response_obj.virtual_events) == 2
        assert sorted(e.id for e in response_obj.virtual_events) == sorted(e.id for e in self._team1_virtual_events)

    async def test_get_virtual_events_with_search_term_team_scope(self) -> None:
        """
        If someone from Team 1 searches for a virtual event owned by Team 2, then there should be no results.
        If someone from Team 2 searches for that same virtual event, then there should be results.
        """

        response = await self.make_request(
            path=ListMyVirtualEventsRequest.config.path,
            payload=ListMyVirtualEventsRequest.RequestBody(
                query=self.getstr("team2 readable_name"),
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
                query=self.getstr("team2 readable_name"),
            ),
            account_id=self._account_team2.id,
            access_token=self._account_team2.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = ListMyVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 1
        assert response_obj.virtual_events[0].id == self._team2_virtual_events[-1].id
