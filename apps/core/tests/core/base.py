import json
import os
import urllib.parse
import uuid
from typing import Any, Protocol, TypeVar
from uuid import UUID

import aiohttp
import pydantic
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql.functions as safunc
from google.cloud.bigquery import SchemaField
from httpx import AsyncClient, Response
from sqlalchemy import literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession

import eave.core.app
import eave.core.internal.database
import eave.core.internal.orm
import eave.stdlib.eave_origins
import eave.stdlib.requests_util
import eave.stdlib.testing_util
import eave.stdlib.typing
from eave.core.graphql.types.search_region_code import SearchRegionCode
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.database import init_database
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.base import get_base_metadata
from eave.core.internal.orm.outing import OutingOrm
from eave.core.internal.orm.survey import SurveyOrm
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.headers import (
    EAVE_ACCOUNT_ID_HEADER,
    EAVE_ORIGIN_HEADER,
    EAVE_REQUEST_ID_HEADER,
)


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
            eave.core.internal.database.async_engine.url.database == "eave-test"
        ), 'Tests perform destructive database operations, and can only be run against the test database (hardcoded to be "eave-test")'

        if not _DB_SETUP:
            print("Running one-time DB setup...")
            await init_database()
            _DB_SETUP = True

        CORE_API_APP_CONFIG.reset_cached_properties()

        await super().asyncSetUp()

        engine = eave.core.internal.database.async_engine.execution_options(isolation_level="READ COMMITTED")
        self.db_session = eave.core.internal.database.async_sessionmaker(engine, expire_on_commit=False)
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
        await eave.core.internal.database.async_engine.dispose()
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

    async def make_request(
        self,
        *,
        path: str,
        payload: pydantic.BaseModel | eave.stdlib.typing.JsonObject | str | bytes | None = None,
        method: str = "POST",
        headers: dict[str, str | None] | None = None,
        cookies: dict[str, str] | None = None,
        origin: eave.stdlib.eave_origins.EaveApp | None = None,
        account_id: uuid.UUID | None = None,
        access_token: str | None = None,
        request_id: uuid.UUID | None = None,
        **kwargs: Any,
    ) -> Response:
        if headers is None:
            headers = {}

        if account_id:
            assert EAVE_ACCOUNT_ID_HEADER not in headers
            headers[EAVE_ACCOUNT_ID_HEADER] = str(account_id)
        else:
            v = headers.get(EAVE_ACCOUNT_ID_HEADER)
            account_id = uuid.UUID(v) if v else None

        if origin:
            assert EAVE_ORIGIN_HEADER not in headers
            headers[EAVE_ORIGIN_HEADER] = origin.value
        else:
            if EAVE_ORIGIN_HEADER not in headers:
                origin = eave.stdlib.eave_origins.EaveApp.eave_dashboard
                headers[EAVE_ORIGIN_HEADER] = origin

        if request_id:
            assert EAVE_REQUEST_ID_HEADER not in headers
            headers[EAVE_REQUEST_ID_HEADER] = str(request_id)
        elif EAVE_REQUEST_ID_HEADER in headers:
            request_id = uuid.UUID(headers[EAVE_REQUEST_ID_HEADER])
        else:
            request_id = uuid.uuid4()
            headers[EAVE_REQUEST_ID_HEADER] = str(request_id)

        request_args: dict[str, Any] = {}

        if not payload:
            encoded_payload = ""
            query_payload = {}
        elif isinstance(payload, pydantic.BaseModel):
            encoded_payload = payload.json()
            query_payload = payload.dict()
        elif isinstance(payload, str):
            # Assumed to be a json-encoded string
            encoded_payload = payload
            query_payload = json.loads(encoded_payload)
        elif isinstance(payload, (bytes, bytearray, memoryview)):
            encoded_payload = payload
            query_payload = {}
        else:
            encoded_payload = json.dumps(payload)
            query_payload = payload

        if method == "GET":
            data = urllib.parse.urlencode(query=query_payload)
            request_args["params"] = data
        else:
            request_args["content"] = encoded_payload

        if access_token and aiohttp.hdrs.AUTHORIZATION not in headers:
            headers[aiohttp.hdrs.AUTHORIZATION] = f"Bearer {access_token}"

        clean_headers = {k: v for (k, v) in headers.items() if v is not None}

        response = await self.httpclient.request(
            method,
            path,
            headers=clean_headers,
            cookies=cookies,
            **request_args,
            **kwargs,
        )

        return response

    async def make_account(
        self,
        session: AsyncSession,
    ) -> AccountOrm:
        account = await AccountOrm.create(
            session=session,
            email=self.anyemail(),
            plaintext_password=self.anystr(),
        )

        return account

    async def get_eave_account(self, session: AsyncSession, /, id: UUID) -> AccountOrm | None:
        acct = await AccountOrm.one_or_none(session=session, params=AccountOrm.QueryParams(id=id))
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
            survey = await SurveyOrm.create(
                session=session,
                visitor_id=self.anyuuid(),
                start_time=self.anydatetime(offset=2 * 60 * 60 * 24),
                search_area_ids=[SearchRegionCode.US_CA_LA1],
                budget=self.anyint(min=0, max=3),
                headcount=self.anyint(min=1, max=2),
            )
            surv_id = survey.id

        outing = await OutingOrm.create(
            session=session,
            visitor_id=self.anyuuid(),
            account_id=act_id,
            survey_id=surv_id,
        )

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
