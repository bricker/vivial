import json
import random
import unittest
import urllib.parse
import uuid
from datetime import datetime
from typing import Any, Optional, Protocol, Tuple, TypeVar
from uuid import UUID, uuid4

import eave.core.app
import eave.core.internal.database as eave_db
import eave.core.internal.orm
import eave.core.internal.orm.account
import eave.core.internal.orm.auth_token
import eave.stdlib.core_api.client
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.eave_origins
import eave.stdlib.exceptions as eave_exceptions
import eave.stdlib.jwt as eave_jwt
import eave.stdlib.signing
import eave.stdlib.util as eave_util
import mockito
import sqlalchemy.orm
import sqlalchemy.sql.functions as safunc
from eave.core import EAVE_API_JWT_ISSUER, EAVE_API_SIGNING_KEY
from eave.core.internal.config import app_config
from eave.core.internal.orm.team import TeamOrm
from httpx import AsyncClient, Response
from sqlalchemy import literal_column, select


class AnyStandardOrm(Protocol):
    id: sqlalchemy.orm.Mapped[UUID]


T = TypeVar("T")
J = TypeVar("J", bound=AnyStandardOrm)

TEST_SIGNING_KEY = eave.stdlib.signing.SigningKeyDetails(
    id="test-key",
    version="1",
    algorithm=eave.stdlib.signing.SigningAlgorithm.RS256,
)

eave_db.async_engine.echo = False  # shhh


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    _testdata: dict[str, Any]
    httpclient: AsyncClient

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    async def asyncSetUp(self) -> None:
        self._testdata = {}

        async with eave_db.async_engine.connect() as db_connection:
            await db_connection.run_sync(eave.core.internal.orm.get_base_metadata().drop_all)
            await db_connection.commit()
            await db_connection.run_sync(eave.core.internal.orm.get_base_metadata().create_all)
            await db_connection.commit()
            # tnames = ",".join([t.name for t in eave.core.internal.orm._get_base_metadata().sorted_tables])
            # await connection.execute(text(f"truncate {tnames}"))

        # transport = httpx.ASGITransport(
        #     app=eave.core.app.app,  # type:ignore
        #     raise_app_exceptions=True,
        # )
        self.httpclient = AsyncClient(
            app=eave.core.app.app,
            base_url=app_config.eave_api_base,
        )

        # Tests should never call out to KMS
        self.mock_signing()

    async def asyncTearDown(self) -> None:
        # mockito.verifyStubbedInvocationsAreUsed()
        mockito.unstub()
        await self.httpclient.aclose()
        await eave_db.async_engine.dispose()

    @staticmethod
    async def mock_coroutine(value: T) -> T:
        return value

    def unwrap(self, value: Optional[T]) -> T:
        assert value is not None
        return value

    def anystring(self, name: Optional[str] = None) -> str:
        if name is None:
            name = str(uuid4())

        if name not in self._testdata:
            data = str(uuid4())
            self._testdata[name] = data

        value: str = self._testdata[name]
        return value

    def anyuuid(self, name: Optional[str] = None) -> UUID:
        if name is None:
            name = str(uuid4())

        if name not in self._testdata:
            data = uuid4()
            self._testdata[name] = data

        value: UUID = self._testdata[name]
        return value

    def anyint(self, name: Optional[str] = None) -> int:
        if name is None:
            name = str(uuid4())

        if name not in self._testdata:
            data = random.randint(0, 9999)
            self._testdata[name] = data

        value: int = self._testdata[name]
        return value

    async def save(self, obj: J) -> J:
        async with eave_db.async_session.begin() as db_session:
            db_session.add(obj)
        return obj

    async def reload(self, obj: J) -> J | None:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        async with eave_db.async_session.begin() as db_session:
            result: J | None = await db_session.scalar(stmt)

        return result

    async def delete(self, obj: AnyStandardOrm) -> None:
        async with eave_db.async_session.begin() as db_session:
            await db_session.delete(obj)

    async def count(self, cls: Any) -> int:
        query = select(safunc.count(cls.id))
        async with eave_db.async_session.begin() as db_session:
            count: int | None = await db_session.scalar(query)

        if count is None:
            count = 0
        return count

    async def make_request(
        self,
        path: str,
        payload: Optional[eave_util.JsonObject] = None,
        method: str = "POST",
        headers: Optional[dict[str, Optional[str]]] = None,
        origin: eave.stdlib.eave_origins.EaveOrigin = eave.stdlib.eave_origins.EaveOrigin.eave_www,
        team_id: Optional[uuid.UUID] = None,
        account_id: Optional[uuid.UUID] = None,
        access_token: Optional[str] = None,
        request_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> Response:
        if headers is None:
            headers = {}

        if team_id:
            headers["eave-team-id"] = str(team_id)

        if account_id:
            headers["eave-account-id"] = str(account_id)

        if origin:
            headers["eave-origin"] = origin.value

        request_id = request_id or uuid.uuid4()
        headers["eave-request-id"] = str(request_id)

        request_args: dict[str, Any] = {}
        encoded_payload = json.dumps(payload) if payload else ""

        if method == "GET":
            data = urllib.parse.urlencode(query=payload or {})
            request_args["params"] = data
        else:
            request_args["content"] = encoded_payload

        if "eave-signature" not in headers:
            signature_message = eave.stdlib.core_api.client.build_message_to_sign(
                method=method,
                url=eave.stdlib.core_api.client.makeurl(path),
                origin=origin,
                payload=encoded_payload,
                request_id=request_id,
                team_id=team_id,
                account_id=account_id,
            )

            signature = eave.stdlib.signing.sign_b64(
                signing_key=eave.stdlib.signing.get_key(signer=origin.value),
                data=signature_message,
            )

            headers["eave-signature"] = signature

        if access_token and "authorization" not in headers:
            headers["authorization"] = f"Bearer {access_token}"

        clean_headers = {k: v for (k, v) in headers.items() if v is not None}

        response = await self.httpclient.request(
            method,
            path,
            headers=clean_headers,
            **request_args,
            **kwargs,
        )

        return response

    def mock_signing(self) -> None:
        def _sign_b64(signing_key: eave.stdlib.signing.SigningKeyDetails, data: str | bytes) -> str:
            value: str = eave_util.b64encode(eave_util.sha256hexdigest(data))
            return value

        def _verify_signature_or_exception(
            signing_key: eave.stdlib.signing.SigningKeyDetails, message: str | bytes, signature: str
        ) -> None:
            if signature != eave_util.b64encode(eave_util.sha256hexdigest(message)):
                raise eave_exceptions.InvalidSignatureError()

        mockito.when2(eave.stdlib.signing.sign_b64, ...).thenAnswer(_sign_b64)
        mockito.when2(eave.stdlib.signing.verify_signature_or_exception, ...).thenAnswer(_verify_signature_or_exception)

    async def mock_auth_token(
        self, account: eave.core.internal.orm.account.AccountOrm
    ) -> Tuple[eave_jwt.JWT, eave_jwt.JWT, eave.core.internal.orm.auth_token.AuthTokenOrm]:
        before_count = await self.count(eave.core.internal.orm.auth_token.AuthTokenOrm)

        access_token = eave_jwt.create_jwt(
            signing_key=EAVE_API_SIGNING_KEY,
            purpose=eave_jwt.JWTPurpose.access,
            iss=EAVE_API_JWT_ISSUER,
            aud=eave.stdlib.eave_origins.EaveOrigin.eave_www.value,
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

        auth_token = eave.core.internal.orm.auth_token.AuthTokenOrm(
            account_id=account.id,
            team_id=account.team_id,
            access_token=eave_util.sha256hexdigest(access_token.to_str()),
            refresh_token=eave_util.sha256hexdigest(refresh_token.to_str()),
            jti=access_token.payload.jti,
            iss=access_token.payload.iss,
            aud=access_token.payload.aud,
            expires=datetime.utcfromtimestamp(float(access_token.payload.exp)),
        )

        auth_token = await self.save(auth_token)
        assert (await self.count(eave.core.internal.orm.auth_token.AuthTokenOrm)) == before_count + 1
        return (access_token, refresh_token, auth_token)

    async def make_team(self) -> TeamOrm:
        team = TeamOrm(name=self.anystring("team name"), document_platform=eave_models.DocumentPlatform.confluence)
        await self.save(team)
        return team

    async def make_account(self, **kwargs: Any) -> eave.core.internal.orm.account.AccountOrm:
        if not (team_id := kwargs.get("team_id")):
            team = await self.make_team()
            team_id = team.id

        account = eave.core.internal.orm.account.AccountOrm(
            auth_provider=kwargs.get("auth_provider", eave_models.AuthProvider.slack),
            auth_id=kwargs.get("auth_id", self.anystring("auth_id")),
            access_token=kwargs.get("oauth_token", self.anystring("oauth_token")),
            refresh_token=kwargs.get("refresh_token", self.anystring("refresh_token")),
            team_id=team_id,
        )
        await self.save(account)
        return account
