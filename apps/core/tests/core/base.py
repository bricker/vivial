import json
import os
import urllib.parse
import uuid
import aiohttp
import pydantic
import sqlalchemy
from typing import Any, Optional, Protocol, TypeVar
from uuid import UUID
from eave.core.internal.database import init_database
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.base import get_base_metadata
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.headers import (
    EAVE_ACCOUNT_ID_HEADER,
    EAVE_ORIGIN_HEADER,
    EAVE_REQUEST_ID_HEADER,
    EAVE_SIG_TS_HEADER,
    EAVE_SIGNATURE_HEADER,
    EAVE_TEAM_ID_HEADER,
)

import eave.stdlib.signing
import eave.stdlib.eave_origins
import eave.stdlib.typing

from eave.stdlib.core_api.models.account import AuthProvider
import eave.stdlib.test_util
import eave.stdlib.requests
import sqlalchemy.orm
import sqlalchemy.sql.functions as safunc
from httpx import AsyncClient, Response
from sqlalchemy import literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession

import eave.core.app
import eave.core.internal
import eave.core.internal.orm
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.stdlib.config import SHARED_CONFIG


class AnyStandardOrm(Protocol):
    id: sqlalchemy.orm.Mapped[UUID]


T = TypeVar("T")
J = TypeVar("J", bound=AnyStandardOrm)

TEST_SIGNING_KEY = eave.stdlib.signing.SigningKeyDetails(
    id="test-key",
    version="1",
    algorithm=eave.stdlib.signing.SigningAlgorithm.RS256,
)

# eave.core.internal.database.async_engine.echo = False  # shhh

_DB_SETUP: bool = False


class BaseTestCase(eave.stdlib.test_util.UtilityBaseTestCase):
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
            base_url=SHARED_CONFIG.eave_public_api_base,
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
        path: str,
        payload: Optional[pydantic.BaseModel | eave.stdlib.typing.JsonObject] = None,
        method: str = "POST",
        headers: Optional[dict[str, Optional[str]]] = None,
        origin: Optional[eave.stdlib.eave_origins.EaveApp] = None,
        team_id: Optional[uuid.UUID] = None,
        account_id: Optional[uuid.UUID] = None,
        access_token: Optional[str] = None,
        request_id: Optional[uuid.UUID] = None,
        sign: bool = True,
        **kwargs: Any,
    ) -> Response:
        if headers is None:
            headers = {}

        if e := headers.get(EAVE_SIG_TS_HEADER):
            eave_sig_ts = int(e)
        else:
            eave_sig_ts = eave.stdlib.signing.make_sig_ts()
            headers[EAVE_SIG_TS_HEADER] = str(eave_sig_ts)

        if team_id:
            assert EAVE_TEAM_ID_HEADER not in headers
            headers[EAVE_TEAM_ID_HEADER] = str(team_id)
        else:
            v = headers.get(EAVE_TEAM_ID_HEADER)
            team_id = uuid.UUID(v) if v else None

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
                origin = eave.stdlib.eave_origins.EaveApp.eave_www
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
        else:
            encoded_payload = json.dumps(payload)
            query_payload = payload

        if method == "GET":
            data = urllib.parse.urlencode(query=query_payload)
            request_args["params"] = data
        else:
            request_args["content"] = encoded_payload

        if sign and EAVE_SIGNATURE_HEADER not in headers:
            origin = origin or eave.stdlib.eave_origins.EaveApp.eave_www
            signature_message = eave.stdlib.signing.build_message_to_sign(
                method=method,
                path=path,
                ts=eave_sig_ts,
                origin=origin,
                audience=eave.stdlib.eave_origins.EaveApp.eave_api,
                payload=encoded_payload,
                request_id=request_id,
                team_id=team_id,
                account_id=account_id,
            )

            signature = eave.stdlib.signing.sign_b64(
                signing_key=eave.stdlib.signing.get_key(signer=origin.value),
                data=signature_message,
            )

            headers[EAVE_SIGNATURE_HEADER] = signature

        if access_token and aiohttp.hdrs.AUTHORIZATION not in headers:
            headers[aiohttp.hdrs.AUTHORIZATION] = f"Bearer {access_token}"

        clean_headers = {k: v for (k, v) in headers.items() if v is not None}

        response = await self.httpclient.request(
            method,
            path,
            headers=clean_headers,
            **request_args,
            **kwargs,
        )

        return response

    async def make_team(self, session: AsyncSession) -> TeamOrm:
        team = await TeamOrm.create(
            session=session,
            name=self.anystr("team name"),
        )

        return team

    async def make_account(
        self,
        session: AsyncSession,
        /,
        team_id: Optional[uuid.UUID] = None,
        auth_provider: Optional[AuthProvider] = None,
        auth_id: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> AccountOrm:
        if not team_id:
            team = await self.make_team(session=session)
            team_id = team.id

        account = await AccountOrm.create(
            session=session,
            team_id=team_id,
            visitor_id=self.anyuuid("account.visitor_id"),
            opaque_utm_params=self.anydict("account.opaque_utm_params", deterministic_keys=True),
            auth_provider=auth_provider or AuthProvider.google,
            auth_id=auth_id or self.anystr("account.auth_id"),
            access_token=access_token or self.anystr("account.oauth_token"),
            refresh_token=refresh_token or self.anystr("account.refresh_token"),
        )

        return account

    async def get_eave_account(self, session: AsyncSession, /, id: UUID) -> AccountOrm | None:
        acct = await AccountOrm.one_or_none(session=session, params=AccountOrm.QueryParams(id=id))
        return acct

    async def get_eave_team(self, session: AsyncSession, /, id: UUID) -> TeamOrm | None:
        acct = await TeamOrm.one_or_none(session=session, team_id=id)
        return acct
