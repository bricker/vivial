import dataclasses
import http
import aiohttp
from eave.collectors.core.datastructures import DataIngestRequestBody, DatabaseOperation, EventType
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER
from eave.core.internal.atoms.models.api_payload_types import BrowserEventPayload, CorrelationContext, SessionProperties
from eave.core.internal.atoms.models.atom_types import BrowserEventAtom
from eave.core.internal.atoms.models.db_views import ClickView, DatabaseEventView, FormSubmissionView, PageViewView
from eave.core.internal.atoms.models.enums import BrowserAction
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT

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
        return dataclasses.asdict(
            BrowserEventPayload(
                timestamp=timestamp,
                action=action,
                corr_ctx=CorrelationContext(
                    visitor_id=visitor_id,
                    session=SessionProperties(
                        id=session_id,
                        start_timestamp=sess_start,
                    ),
                    traffic_source=None,
                    account=None,
                    extra=None,
                ),
                event_id=None,
                extra=None,
                target=None,
                device=None,
                current_page=None,
            )
        )

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
                    EventType.browser_event: [
                        # misusing session_start_timestamp as an event_id for testing assertion convenience
                        self._build_browser_atom(
                            sess_start=1,
                            visitor_id="456",
                            session_id="f4",
                            timestamp=13,
                            action=BrowserAction.PAGE_VIEW,
                        ),
                        self._build_browser_atom(
                            sess_start=2, visitor_id="456", session_id="f4", timestamp=7, action=BrowserAction.PAGE_VIEW
                        ),  # redirect
                        self._build_browser_atom(
                            sess_start=3, visitor_id="123", session_id="a3", timestamp=2, action=BrowserAction.CLICK
                        ),
                        self._build_browser_atom(
                            sess_start=4, visitor_id="789", session_id="e1", timestamp=3, action=BrowserAction.CLICK
                        ),
                        self._build_browser_atom(
                            sess_start=5, visitor_id="456", session_id="f4", timestamp=9, action=BrowserAction.CLICK
                        ),
                        self._build_browser_atom(
                            sess_start=6, visitor_id="456", session_id="f4", timestamp=6, action=BrowserAction.PAGE_VIEW
                        ),  # redirect
                        self._build_browser_atom(
                            sess_start=7, visitor_id="123", session_id="a3", timestamp=3, action=BrowserAction.PAGE_VIEW
                        ),
                        self._build_browser_atom(
                            sess_start=8, visitor_id="123", session_id="a4", timestamp=6, action=BrowserAction.PAGE_VIEW
                        ),
                        self._build_browser_atom(
                            sess_start=9, visitor_id="456", session_id="f4", timestamp=8, action=BrowserAction.PAGE_VIEW
                        ),
                        self._build_browser_atom(
                            sess_start=10, visitor_id="456", session_id="f4", timestamp=10, action=BrowserAction.CLICK
                        ),
                        self._build_browser_atom(
                            sess_start=11,
                            visitor_id="123",
                            session_id="a3",
                            timestamp=1,
                            action=BrowserAction.PAGE_VIEW,
                        ),
                        self._build_browser_atom(
                            sess_start=12, visitor_id="456", session_id="f4", timestamp=11, action=BrowserAction.CLICK
                        ),
                        self._build_browser_atom(
                            sess_start=13,
                            visitor_id="456",
                            session_id="f4",
                            timestamp=12,
                            action=BrowserAction.PAGE_VIEW,
                        ),  # redirect
                        self._build_browser_atom(
                            sess_start=14, visitor_id="456", session_id="f5", timestamp=19, action=BrowserAction.CLICK
                        ),
                        self._build_browser_atom(
                            sess_start=15,
                            visitor_id="789",
                            session_id="e1",
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
        # (i.e. automatic redirects w/o any interaction in-between) are filtered out
        assert len(rows) == 12, "Incorrect number of redirect events filtered out"
        # misusing session_start_timestamp as an event_id for testing assertion convenience
        vevent_ids = [row["session_start_timestamp"] for row in rows]
        assert 13 not in vevent_ids, "Failed to filter out a redirect event"
        assert 6 not in vevent_ids, "Failed to filter out a redirect event"
        assert 2 not in vevent_ids, "Failed to filter out a redirect event"
