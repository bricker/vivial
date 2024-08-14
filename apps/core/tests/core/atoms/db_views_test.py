import dataclasses
import http
import aiohttp
from eave.collectors.core.datastructures import DataIngestRequestBody, DatabaseOperation, EventType
from eave.core.internal.atoms.models.api_payload_types import BrowserEventPayload, CorrelationContext, SessionProperties
from eave.core.internal.atoms.models.atom_types import BrowserEventAtom
from eave.core.internal.atoms.models.db_views import ClickView, DatabaseEventView, FormSubmissionView, PageViewView
from eave.core.internal.atoms.models.enums import BrowserAction

from ..bq_tests_base import BigQueryTestsBase


class TestDatabaseEventView(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_init(self) -> None:
        view = DatabaseEventView(event_table_name=self.anystr(), event_operation=DatabaseOperation.INSERT)

        # Lazy checks for runtime errors.
        assert view.view_id is not None
        assert view.friendly_name is not None
        assert view.description is not None
        assert view.schema
        assert view.build_view_query(dataset_id=self.anyhex())
        assert view.schema_fields
        assert view.compiled_selectors
        assert view.sql_sanitized_fq_table(dataset_id=self.anyhex(), table_id=self.anyhex())


class TestClickView(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_init(self) -> None:
        view = ClickView()

        assert view.view_id is not None
        assert view.friendly_name is not None
        assert view.description is not None
        assert view.schema
        assert view.build_view_query(dataset_id=self.anyhex())
        assert view.schema_fields
        assert view.compiled_selectors
        assert view.sql_sanitized_fq_table(dataset_id=self.anyhex(), table_id=self.anyhex())


class TestFormSubmissionView(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_init(self) -> None:
        view = FormSubmissionView()

        assert view.view_id is not None
        assert view.friendly_name is not None
        assert view.description is not None
        assert view.schema
        assert view.build_view_query(dataset_id=self.anyhex())
        assert view.schema_fields
        assert view.compiled_selectors
        assert view.sql_sanitized_fq_table(dataset_id=self.anyhex(), table_id=self.anyhex())


class TestPageViewView(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    def _build_browser_atom(
        self,
        sess_start: float,
        visitor_id: str,
        session_id: str,
        timestamp: float,
        action: BrowserAction,
    ) -> dict:
        return {
            "timestamp": timestamp,
            "corr_ctx": {
                "_eave.session": f'{{"id": "{session_id}", "start_timestamp": {sess_start}}}',
                "_eave.visitor_id": visitor_id,
            },
            "action": action,
        }

    async def test_init(self) -> None:
        view = PageViewView()

        assert view.view_id is not None
        assert view.friendly_name is not None
        assert view.description is not None
        assert view.schema
        assert view.build_view_query(dataset_id=self.anyhex())
        assert view.schema_fields
        assert view.compiled_selectors
        assert view.sql_sanitized_fq_table(dataset_id=self.anyhex(), table_id=self.anyhex())

    async def test_view_query_removes_same_session_redirects(self) -> None:
        # GIVEN atoms table contains consecutive page_view atoms
        response = await self.make_request(
            method="POST",
            path=f"/public/ingest/browser?clientId={self.client_credentials.id}",
            headers={
                aiohttp.hdrs.ORIGIN: "https://eave.test",
            },
            payload=DataIngestRequestBody(
                events={
                    # click and page view events are intermingled to test that page_views with
                    # interactions in between dont count as redirects
                    EventType.browser_event: [
                        # misusing session_start_timestamp as an event_id for testing assertion convenience
                        self._build_browser_atom(
                            sess_start=1,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="1f956e03-b7a3-4bed-85f5-316a07a0b27b",
                            timestamp=13,
                            action=BrowserAction.PAGE_VIEW,
                        ),
                        self._build_browser_atom(
                            sess_start=2,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="1f956e03-b7a3-4bed-85f5-316a07a0b27b",
                            timestamp=7,
                            action=BrowserAction.PAGE_VIEW,
                        ),  # redirect
                        self._build_browser_atom(
                            sess_start=3,
                            visitor_id="0e7e2402-ef3d-4c7c-b400-64b8c94b636b",
                            session_id="ffff1f83-4e4c-4e61-8ba8-c0be766a663f",
                            timestamp=2,
                            action=BrowserAction.CLICK,
                        ),
                        self._build_browser_atom(
                            sess_start=4,
                            visitor_id="49fb0f21-1613-45a0-a336-dea179f0ae2b",
                            session_id="5221283f-01e7-4483-84ef-1694ee4a22ae",
                            timestamp=3,
                            action=BrowserAction.CLICK,
                        ),
                        self._build_browser_atom(
                            sess_start=5,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="1f956e03-b7a3-4bed-85f5-316a07a0b27b",
                            timestamp=9,
                            action=BrowserAction.CLICK,
                        ),
                        self._build_browser_atom(
                            sess_start=6,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="1f956e03-b7a3-4bed-85f5-316a07a0b27b",
                            timestamp=6,
                            action=BrowserAction.PAGE_VIEW,
                        ),  # redirect
                        self._build_browser_atom(
                            sess_start=7,
                            visitor_id="0e7e2402-ef3d-4c7c-b400-64b8c94b636b",
                            session_id="ffff1f83-4e4c-4e61-8ba8-c0be766a663f",
                            timestamp=3,
                            action=BrowserAction.PAGE_VIEW,
                        ),
                        self._build_browser_atom(
                            sess_start=8,
                            visitor_id="0e7e2402-ef3d-4c7c-b400-64b8c94b636b",
                            session_id="49cadfb7-71fb-45b7-a1c6-68d3f378c69e",
                            timestamp=6,
                            action=BrowserAction.PAGE_VIEW,
                        ),
                        self._build_browser_atom(
                            sess_start=9,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="1f956e03-b7a3-4bed-85f5-316a07a0b27b",
                            timestamp=8,
                            action=BrowserAction.PAGE_VIEW,
                        ),
                        self._build_browser_atom(
                            sess_start=10,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="1f956e03-b7a3-4bed-85f5-316a07a0b27b",
                            timestamp=10,
                            action=BrowserAction.CLICK,
                        ),
                        self._build_browser_atom(
                            sess_start=11,
                            visitor_id="0e7e2402-ef3d-4c7c-b400-64b8c94b636b",
                            session_id="ffff1f83-4e4c-4e61-8ba8-c0be766a663f",
                            timestamp=1,
                            action=BrowserAction.PAGE_VIEW,
                        ),
                        self._build_browser_atom(
                            sess_start=12,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="1f956e03-b7a3-4bed-85f5-316a07a0b27b",
                            timestamp=11,
                            action=BrowserAction.CLICK,
                        ),
                        self._build_browser_atom(
                            sess_start=13,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="1f956e03-b7a3-4bed-85f5-316a07a0b27b",
                            timestamp=12,
                            action=BrowserAction.PAGE_VIEW,
                        ),  # redirect
                        self._build_browser_atom(
                            sess_start=14,
                            visitor_id="6eb1d2aa-abb5-400c-a246-2ea74bec2576",
                            session_id="b5da591b-a2e2-4160-ba07-ead902850699",
                            timestamp=19,
                            action=BrowserAction.CLICK,
                        ),
                        self._build_browser_atom(
                            sess_start=15,
                            visitor_id="49fb0f21-1613-45a0-a336-dea179f0ae2b",
                            session_id="5221283f-01e7-4483-84ef-1694ee4a22ae",
                            timestamp=4,
                            action=BrowserAction.PAGE_VIEW,
                        ),
                    ],
                },
            ).to_dict(),
        )

        assert response.status_code == http.HTTPStatus.OK
        assert self.team_bq_dataset_exists()
        assert self.team_bq_table_exists(BrowserEventAtom.table_def().table_id)

        # WHEN page_view bq view query loads data
        pv = PageViewView()
        dataset = self.get_team_bq_dataset()
        assert dataset
        query = pv.build_view_query(dataset_id=dataset.dataset_id)
        rows = list(self.bq_client.query_and_wait(query=query))

        # THEN consecutive page_view events by the same visitor in the same session
        # (i.e. automatic redirects w/o any interaction in-between) are filtered out,
        # along with the CLICK action events.
        assert len(rows) == 6, "Incorrect number of browser events filtered out"
        # misusing session_start_timestamp as an event_id for testing assertion convenience
        vevent_ids = sorted([row["session_start_timestamp"].timestamp() for row in rows])
        assert vevent_ids == [1, 7, 8, 9, 11, 15], "BQ View did not contain exactly the expected events"
