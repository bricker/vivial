import os
from typing import override

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import eave.core.app
import eave.core.database
import eave.core.orm
import eave.stdlib.typing
from eave.core._database_setup import get_base_metadata, reset_database
from eave.core.config import CORE_API_APP_CONFIG
from eave.stdlib.testing_util import UtilityBaseTestCase

from ._helpers.google_places_mocks_mixin import GooglePlacesMocksMixin
from ._helpers.graphql_mixin import GraphQLMixin
from ._helpers.http_client_mixin import HTTPClientMixin
from ._helpers.orm_helpers_mixin import OrmHelpersMixin
from ._helpers.random_instance_mixin import RandomInstanceMixin
from ._helpers.stripe_mocks_mixin import StripeMocksMixin

_db_setup: bool = False

# eave.core.database.async_engine.echo = True


class BaseTestCase(
    RandomInstanceMixin,
    GraphQLMixin,
    OrmHelpersMixin,
    GooglePlacesMocksMixin,
    StripeMocksMixin,
    UtilityBaseTestCase,
    HTTPClientMixin,
):
    db_session: async_sessionmaker[AsyncSession]  # pyright: ignore [reportUninitializedInstanceVariable]

    @override
    async def asyncSetUp(self) -> None:
        global _db_setup

        # Attempt to prevent running destructive database operations against non-test database
        assert os.environ["EAVE_ENV"] == "test", "Tests must be run with EAVE_ENV=test"
        assert (
            eave.core.database.async_engine.url.database == "eave-test"
        ), 'Tests perform destructive database operations, and can only be run against the test database (hardcoded to be "eave-test")'

        if not _db_setup:
            print("Running one-time DB setup...")
            await reset_database()
            _db_setup = True

        CORE_API_APP_CONFIG.reset_cached_properties()

        await super().asyncSetUp()

        engine = eave.core.database.async_engine.execution_options(isolation_level="READ COMMITTED")
        self.db_session = eave.core.database.async_sessionmaker(engine, expire_on_commit=False)

    @override
    async def cleanup(self) -> None:
        await super().cleanup()

        tnames = ",".join([t.name for t in get_base_metadata().sorted_tables])
        conn = await self.db_session().connection()
        await conn.execute(text(f"TRUNCATE {tnames} CASCADE").execution_options(autocommit=True))
        await conn.commit()
        await conn.close()
        await eave.core.database.async_engine.dispose()
