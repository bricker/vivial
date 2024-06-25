from tests.core.bq_tests_base import BigQueryTestsBase

from eave.collectors.core.datastructures import DatabaseOperation
from eave.core.internal.atoms.db_views import ClickView, DatabaseEventView, FormSubmissionView, PageViewView


class TestDatabaseEventView(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_init(self) -> None:
        view = DatabaseEventView(
            dataset_id=self.anystr(), event_table_name=self.anystr(), event_operation=DatabaseOperation.INSERT
        )

        # Lazy checks for runtime errors.
        assert view.view_id is not None
        assert view.friendly_name is not None
        assert view.description is not None
        assert view.dataset_id is not None
        assert view.schema
        assert view.view_query
        assert view.schema_fields
        assert view.compiled_selectors
        assert view.sql_sanitized_fq_table(table_id=self.anystr())


class TestClickView(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_init(self) -> None:
        view = ClickView(
            dataset_id=self.anystr(),
        )

        assert view.view_id is not None
        assert view.friendly_name is not None
        assert view.description is not None
        assert view.dataset_id is not None
        assert view.schema
        assert view.view_query
        assert view.schema_fields
        assert view.compiled_selectors
        assert view.sql_sanitized_fq_table(table_id=self.anystr())


class TestFormSubmissionView(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_init(self) -> None:
        view = FormSubmissionView(
            dataset_id=self.anystr(),
        )

        assert view.view_id is not None
        assert view.friendly_name is not None
        assert view.description is not None
        assert view.dataset_id is not None
        assert view.schema
        assert view.view_query
        assert view.schema_fields
        assert view.compiled_selectors
        assert view.sql_sanitized_fq_table(table_id=self.anystr())


class TestPageViewView(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_init(self) -> None:
        view = PageViewView(
            dataset_id=self.anystr(),
        )

        assert view.view_id is not None
        assert view.friendly_name is not None
        assert view.description is not None
        assert view.dataset_id is not None
        assert view.schema
        assert view.view_query
        assert view.schema_fields
        assert view.compiled_selectors
        assert view.sql_sanitized_fq_table(table_id=self.anystr())
