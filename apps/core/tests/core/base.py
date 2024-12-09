import os
import unittest.mock
from http import HTTPStatus
from typing import Any, Protocol, TypeVar
from uuid import UUID

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql.functions as safunc
from google.maps.places_v1.types import Place
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy import literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import ExecutionResult

import eave.core.app
import eave.core.database
import eave.core.orm
import eave.stdlib.testing_util
import eave.stdlib.typing
from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME
from eave.core.config import CORE_API_APP_CONFIG, JWT_AUDIENCE, JWT_ISSUER
from eave.core.database import init_database
from eave.core.orm.account import AccountOrm
from eave.core.orm.base import get_base_metadata
from eave.core.orm.outing import OutingOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget
from eave.dev_tooling.constants import EAVE_HOME
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.jwt import JWTPurpose, create_jws
from eave.stdlib.time import ONE_YEAR_IN_MINUTES


class AnyStandardOrm(Protocol):
    id: sqlalchemy.orm.Mapped[UUID]


T = TypeVar("T")
J = TypeVar("J", bound=AnyStandardOrm)

# eave.core.internal.database.async_engine.echo = False  # shhh

_DB_SETUP: bool = False


class MockPlacesResponse:
    places: list[Place]

    def __init__(self, places: list[Place]) -> None:
        self.places = places


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
        self.mock_google_places()

        engine = eave.core.database.async_engine.execution_options(isolation_level="READ COMMITTED")
        self.db_session = eave.core.database.async_sessionmaker(engine, expire_on_commit=False)
        # self.db_session = eave.core.internal.database.async_session

        transport = ASGITransport(
            app=eave.core.app.app,  # type:ignore
            raise_app_exceptions=True,
        )
        self.httpclient = AsyncClient(
            base_url=SHARED_CONFIG.eave_api_base_url_public,
            transport=transport,
        )

        self._gql_cache = {}

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

    def load_graphql_query(self, name: str) -> str:
        if name not in self._gql_cache:
            with open(f"{EAVE_HOME}/apps/core/tests/core/resolvers/graphql/{name}.graphql") as f:
                self._gql_cache[name] = f.read()

        return self._gql_cache[name]

    async def save(self, session: AsyncSession, /, obj: J) -> J:
        session.add(obj)
        return obj

    async def reload(self, session: AsyncSession, /, obj: J) -> J | None:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        result: J | None = await session.scalar(stmt)
        return result

    async def delete(self, session: AsyncSession, /, obj: AnyStandardOrm) -> None:
        await session.delete(obj)

    async def count(self, session: AsyncSession, /, cls: type[AnyStandardOrm]) -> int:
        query = select(safunc.count(cls.id))
        count: int | None = await session.scalar(query)

        if count is None:
            count = 0
        return count

    def parse_graphql_response(self, response: Response) -> ExecutionResult:
        j = response.json()

        result = ExecutionResult(
            data=j.get("data"),
            errors=j.get("errors"),
        )

        return result

    async def make_graphql_request(
        self, query_name: str, variables: dict[str, Any], *, account_id: UUID | None = None
    ) -> Response:
        cookies: dict[str, str] = {}

        if account_id:
            jws = create_jws(
                purpose=JWTPurpose.ACCESS,
                issuer=JWT_ISSUER,
                audience=JWT_AUDIENCE,
                subject=str(account_id),
                jwt_id=self.anystr(),
                max_age_minutes=ONE_YEAR_IN_MINUTES,
            )

            cookies[ACCESS_TOKEN_COOKIE_NAME] = jws

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": self.load_graphql_query(query_name),
                "variables": variables,
            },
            cookies=cookies,
        )

        assert response.status_code == HTTPStatus.OK
        return response

    async def make_account(
        self,
        session: AsyncSession,
    ) -> AccountOrm:
        account = await AccountOrm.build(
            email=self.anyemail("make_account.email"),
            plaintext_password=self.anystr("make_account.plaintext_password"),
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
                start_time_utc=self.anydatetime(offset=2 * 60 * 60 * 24),
                timezone=self.anytimezone(),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1, max=2),
            ).save(session)
            surv_id = survey.id

        outing = await OutingOrm.build(
            visitor_id=self.anyuuid(),
            account_id=act_id,
            survey_id=surv_id,
        ).save(session)

        return outing

    def mock_google_places(self) -> None:
        self.patch(
            name="google places searchNearby",
            patch=unittest.mock.patch(
                "google.maps.places_v1.services.places.async_client.PlacesAsyncClient.search_nearby"
            ),
            return_value=MockPlacesResponse([]),
        )
