import os
from typing import Any, Protocol, TypeVar
from uuid import UUID

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql.functions as safunc
from google.cloud.bigquery import SchemaField
from httpx import AsyncClient
from sqlalchemy import literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession

import eave.core.app
import eave.core.database
import eave.core.orm
import eave.stdlib.testing_util
import eave.stdlib.typing
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.database import init_database
from eave.core.orm.account import AccountOrm
from eave.core.orm.base import get_base_metadata
from eave.core.orm.outing import OutingOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.stdlib.config import SHARED_CONFIG


class AnyStandardOrm(Protocol):
    id: sqlalchemy.orm.Mapped[UUID]


T = TypeVar("T")
J = TypeVar("J", bound=AnyStandardOrm)

# eave.core.internal.database.async_engine.echo = False  # shhh

_DB_SETUP: bool = False


class BaseTestCase(eave.stdlib.testing_util.UtilityBaseTestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    async def asyncSetUp(self) -> None:
        global _DB_SETUP

        # Attempt to prevent running destructive database operations against non-test database
        assert os.environ["EAVE_ENV"] == "test", "Tests must be run with EAVE_ENV=test"
        assert (
            eave.core.database.async_engine.url.database == "eave-test"
        ), 'Tests perform destructive database operations, and can only be run against the test database (hardcoded to be "eave-test")'

        if not _DB_SETUP:
            print("Running one-time DB setup...")
            await init_database()
            _DB_SETUP = True

        CORE_API_APP_CONFIG.reset_cached_properties()

        await super().asyncSetUp()

        engine = eave.core.database.async_engine.execution_options(isolation_level="READ COMMITTED")
        self.db_session = eave.core.database.async_sessionmaker(engine, expire_on_commit=False)
        # self.db_session = eave.core.internal.database.async_session

        # transport = httpx.ASGITransport(
        #     app=eave.core.app.app,  # type:ignore
        #     raise_app_exceptions=True,
        # )
        self.httpclient = AsyncClient(
            app=eave.core.app.app,
            base_url=SHARED_CONFIG.eave_api_base_url_public,
            # transport=transport,
        )

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    async def cleanup(self) -> None:
        await super().cleanup()

        tnames = ",".join([t.name for t in get_base_metadata().sorted_tables])
        conn = await self.db_session().connection()
        await conn.execute(text(f"TRUNCATE {tnames} CASCADE").execution_options(autocommit=True))
        await conn.commit()
        await conn.close()
        await eave.core.database.async_engine.dispose()
        await self.httpclient.aclose()

    async def save(self, session: AsyncSession, /, obj: J) -> J:
        session.add(obj)
        return obj

    async def reload(self, session: AsyncSession, /, obj: J) -> J | None:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        result: J | None = await session.scalar(stmt)
        return result

    async def delete(self, session: AsyncSession, /, obj: AnyStandardOrm) -> None:
        await session.delete(obj)

    async def count(self, session: AsyncSession, /, cls: Any) -> int:
        query = select(safunc.count(cls.id))
        count: int | None = await session.scalar(query)

        if count is None:
            count = 0
        return count

    async def make_account(
        self,
        session: AsyncSession,
    ) -> AccountOrm:
        account = await AccountOrm.build(
            email=self.anyemail(),
            plaintext_password=self.anystr(),
        ).save(session)

        return account

    async def get_eave_account(self, session: AsyncSession, /, id: UUID) -> AccountOrm | None:
        acct = await AccountOrm.get_one(session, id)
        return acct

    async def make_outing(
        self,
        session: AsyncSession,
        account_id: UUID | None = None,
        survey_id: UUID | None = None,
    ) -> OutingOrm:
        act_id = account_id
        if act_id is None:
            account = await self.make_account(session=session)
            act_id = account.id

        surv_id = survey_id
        if surv_id is None:
            survey = await SurveyOrm.build(
                visitor_id=self.anyuuid(),
                start_time=self.anydatetime(offset=2 * 60 * 60 * 24),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=self.anyint(min=0, max=3),
                headcount=self.anyint(min=1, max=2),
            ).save(session)
            surv_id = survey.id

        outing = await OutingOrm.build(
            visitor_id=self.anyuuid(),
            account_id=act_id,
            survey_id=surv_id,
        ).save(session)

        return outing


def assert_schemas_match(a: tuple[SchemaField, ...], b: tuple[SchemaField, ...]) -> None:
    assert len(a) == len(b), "Field lengths do not match."

    sorteda = sorted(a, key=lambda f: f.name)
    sortedb = sorted(b, key=lambda f: f.name)

    for idx, fielda in enumerate(sorteda):
        fieldb = sortedb[idx]
        assert fieldb.name == fielda.name, f"{fieldb.name} does not match expected {fielda.name}"
        assert (
            fieldb.field_type == fielda.field_type
        ), f"{fieldb.field_type} does not match expected {fielda.field_type}"
        assert fieldb.mode == fielda.mode, f"{fieldb.mode} does not match expected {fielda.mode}"
        assert (
            fieldb.default_value_expression == fielda.default_value_expression
        ), f"{fieldb.default_value_expression} does not match expected {fielda.default_value_expression}"
        assert_schemas_match(fielda.fields, fieldb.fields)
