from ..bq_tests_base import BigQueryTestsBase


class TestBigQueryTableHandle(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_create_bq_view(self):
        self.fail("not implemented")
