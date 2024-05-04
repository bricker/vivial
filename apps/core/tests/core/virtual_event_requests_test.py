from http import HTTPStatus

from eave.stdlib.core_api.models.virtual_event import VirtualEventQueryInput
from eave.stdlib.core_api.operations.team import GetTeamRequest
from eave.stdlib.core_api.operations.virtual_event import GetVirtualEventsRequest

from eave.core.internal.orm.virtual_event import VirtualEventOrm

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
                await VirtualEventOrm.create(
                    session=s,
                    team_id=self._team2.id,
                    view_id=self.anystr(f"view_id {i}"),
                    description=self.anystr(f"description {i}"),
                    readable_name=self.anystr(f"readable_name {i}"),
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
            path=GetVirtualEventsRequest.config.path,
            payload=GetVirtualEventsRequest.RequestBody(
                virtual_events=VirtualEventQueryInput(
                    search_term=self.getstr("view_id 0"),
                )
            ),
            team_id=self._team1.id,
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 1
        assert response_obj.virtual_events[0].id == self._team1_virtual_events[0].id

    async def test_get_virtual_events_with_search_term_no_match(self) -> None:
        response = await self.make_request(
            path=GetVirtualEventsRequest.config.path,
            payload=GetVirtualEventsRequest.RequestBody(
                virtual_events=VirtualEventQueryInput(
                    search_term=self.anystr(),
                )
            ),
            team_id=self._team1.id,
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 0

    async def test_get_virtual_events_with_no_search_term(self) -> None:
        response = await self.make_request(
            path=GetVirtualEventsRequest.config.path,
            payload=None,
            team_id=self._team1.id,
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 2
        assert sorted(response_obj.virtual_events, key=lambda v: v.id) == sorted(self._team1_virtual_events, key=lambda v: v.id)

    async def test_get_virtual_events_mismatched_team_id(self) -> None:
        response = await self.make_request(
            path=GetVirtualEventsRequest.config.path,
            payload=None,
            team_id=self._team2.id,
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_get_virtual_events_with_no_search_term_team_scope(self) -> None:
        response = await self.make_request(
            path=GetVirtualEventsRequest.config.path,
            payload=GetVirtualEventsRequest.RequestBody(
                virtual_events=VirtualEventQueryInput(
                    search_term=self.getstr("team2 view_id"),
                )
            ),
            team_id=self._team1.id,
            account_id=self._account_team1.id,
            access_token=self._account_team1.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 0

        response = await self.make_request(
            path=GetVirtualEventsRequest.config.path,
            payload=GetVirtualEventsRequest.RequestBody(
                virtual_events=VirtualEventQueryInput(
                    search_term=self.getstr("team2 view_id"),
                )
            ),
            team_id=self._team2.id,
            account_id=self._account_team2.id,
            access_token=self._account_team2.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetVirtualEventsRequest.ResponseBody(**response.json())
        assert len(response_obj.virtual_events) == 1
        assert response_obj.virtual_events[0].id == self._team2_virtual_events[-1].id

