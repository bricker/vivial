import json
import random
import unittest
import urllib.parse
from datetime import datetime
from typing import Any, Optional, Protocol, Tuple, TypeVar
from uuid import UUID, uuid4

import eave.core.app
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.jwt as eave_jwt
import eave.stdlib.signing
import eave.stdlib.util as eave_util
import httpx
import mockito
import sqlalchemy.sql.functions as safunc
from eave.core import EAVE_API_JWT_ISSUER, EAVE_API_SIGNING_KEY
from eave.core.internal.config import app_config
from eave.core.internal.database import engine, get_async_session
from eave.stdlib.eave_origins import EaveOrigin
from httpx import AsyncClient, Response
from sqlalchemy import literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped


class AnyStandardOrm(Protocol):
    id: Mapped[UUID]


T = TypeVar("T")
J = TypeVar("J", bound=AnyStandardOrm)

TEST_SIGNING_KEY = eave.stdlib.signing.SigningKeyDetails(
    id="test-key",
    version="1",
    algorithm=eave.stdlib.signing.SigningAlgorithm.RS256,
)


async def mock_coroutine(value: T) -> T:
    return value


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    _testdata = dict[str, Any]()
    httpclient: AsyncClient
    db_session: AsyncSession

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    async def asyncSetUp(self) -> None:
        self._testdata.clear()

        engine.echo = False  # shhh
        self.db_session = get_async_session()
        self.db_session.begin()
        connection = await self.db_session.connection()
        assert connection.engine.url.database != "eave"
        await connection.run_sync(eave_orm.Base.metadata.drop_all)
        await connection.run_sync(eave_orm.Base.metadata.create_all)

        transport = httpx.ASGITransport(
            app=eave.core.app.app,  # type:ignore
            raise_app_exceptions=False,
        )
        self.httpclient = AsyncClient(
            transport=transport,
            base_url=app_config.eave_api_base,
        )

    async def asyncTearDown(self) -> None:
        mockito.verifyStubbedInvocationsAreUsed()
        mockito.unstub()
        await self.httpclient.aclose()
        await self.db_session.close()

    def unwrap(self, value: Optional[T]) -> T:
        assert value is not None
        return value

    def anystring(self, name: str) -> str:
        if name not in self._testdata:
            data = str(uuid4())
            self._testdata[name] = data

        value: str = self._testdata[name]
        return value

    def anyuuid(self, name: str) -> UUID:
        if name not in self._testdata:
            data = uuid4()
            self._testdata[name] = data

        value: UUID = self._testdata[name]
        return value

    def anyint(self, name: str) -> int:
        if name not in self._testdata:
            data = random.randint(0, 9999)
            self._testdata[name] = data

        value: int = self._testdata[name]
        return value

    async def save(self, obj: J) -> J:
        self.db_session.add(obj)
        await self.db_session.commit()
        return obj

    async def reload(self, obj: J) -> J | None:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        result = await self.db_session.scalar(stmt)
        return result

    async def delete(self, obj: AnyStandardOrm) -> None:
        await self.db_session.delete(obj)
        await self.db_session.commit()

    async def count(self, cls: AnyStandardOrm) -> int:
        query = select(safunc.count(cls.id))
        count = await self.db_session.scalar(query)
        if count is None:
            count = 0
        return count

    async def make_request(
        self,
        url: str,
        payload: Optional[eave_util.JsonObject] = None,
        method: str = "POST",
        headers: dict[str, str] = {},
        access_token: Optional[eave_jwt.JWT] = None,
        **kwargs: Any,
    ) -> Response:
        request_args: dict[str, Any] = {}

        if payload is not None:
            if method == "GET":
                data = urllib.parse.urlencode(query=payload)
                request_args["params"] = data
            else:
                data = json.dumps(payload)
                request_args["content"] = data

            if (team_id := headers.get("eave-team-id")) is not None:
                headers["eave-team-id"] = team_id

            headers["eave-signature"] = eave.stdlib.signing.sign_b64(signing_key=TEST_SIGNING_KEY, data=data)
            headers["eave-origin"] = EaveOrigin.eave_www.value

            if access_token:
                headers["authorization"] = f"Bearer {access_token}"

        response = await self.httpclient.request(
            method,
            url,
            headers=headers,
            **request_args,
            **kwargs,
        )

        return response

    def mock_signing(self) -> None:
        def sign_b64(signing_key: eave.stdlib.signing.SigningKeyDetails, data: str | bytes) -> str:
            value: str = eave_util.b64encode(eave_util.sha256hexdigest(data))
            return value

        def verify_signature_or_exception(
            signing_key: eave.stdlib.signing.SigningKeyDetails, message: str | bytes, signature: str
        ) -> None:
            assert signature == sign_b64(signing_key=signing_key, data=message)

        mockito.patch(eave.stdlib.signing.sign_b64, sign_b64)
        mockito.patch(eave.stdlib.signing.verify_signature_or_exception, verify_signature_or_exception)

    async def mock_auth_token(
        self, account: eave_orm.AccountOrm
    ) -> Tuple[eave_jwt.JWT, eave_jwt.JWT, eave_orm.AuthTokenOrm]:
        before_count = await self.count(eave_orm.AuthTokenOrm)

        access_token = eave_jwt.create_jwt(
            signing_key=EAVE_API_SIGNING_KEY,
            purpose=eave_jwt.JWTPurpose.access,
            iss=EAVE_API_JWT_ISSUER,
            aud=EaveOrigin.eave_www.value,
            sub=str(account.id),
        )

        refresh_token = eave_jwt.create_jwt(
            signing_key=EAVE_API_SIGNING_KEY,
            purpose=eave_jwt.JWTPurpose.refresh,
            iss=EAVE_API_JWT_ISSUER,
            aud=access_token.payload.aud,
            sub=access_token.payload.sub,
            iat=access_token.payload.iat,
            nbf=access_token.payload.nbf,
            jti=access_token.payload.jti,
            exp_minutes=60,
        )

        auth_token = eave_orm.AuthTokenOrm(
            account_id=account.id,
            team_id=account.team_id,
            access_token=eave_util.sha256hexdigest(access_token.to_str()),
            refresh_token=eave_util.sha256hexdigest(refresh_token.to_str()),
            jti=access_token.payload.jti,
            iss=access_token.payload.iss,
            aud=access_token.payload.aud,
            expires=datetime.utcfromtimestamp(float(access_token.payload.exp)),
        )

        self.db_session.add(auth_token)
        await self.db_session.commit()

        assert (await self.count(eave_orm.AuthTokenOrm)) == before_count + 1
        return (access_token, refresh_token, auth_token)

    async def make_team(self) -> eave_orm.TeamOrm:
        team = eave_orm.TeamOrm(name=self.anystring("team name"))
        await self.save(team)
        return team

    async def make_account(self, **kwargs: Any) -> eave_orm.AccountOrm:
        team = await self.make_team()
        account = eave_orm.AccountOrm(
            auth_provider=kwargs.get("auth_provider", eave_models.AuthProvider.slack),
            auth_id=kwargs.get("auth_id", self.anystring("auth_id")),
            oauth_token=kwargs.get("oauth_token", self.anystring("oauth_token")),
            team_id=team.id,
        )
        await self.save(account)
        return account
