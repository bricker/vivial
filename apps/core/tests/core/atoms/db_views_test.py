from eave.collectors.core.datastructures import DatabaseOperation
from eave.core.internal.atoms.models.db_views import ClickView, DatabaseEventView, FormSubmissionView, PageViewView

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
