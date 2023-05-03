import json
import os
import random
import typing
import unittest
import unittest.mock
import urllib.parse
import uuid
from datetime import datetime
from typing import Any, Optional, Protocol, Tuple, TypeVar
from uuid import UUID, uuid4

import eave.core.app
import eave.core.internal
import eave.core.internal.orm
import eave.core.internal.orm.base
import eave.stdlib
import eave.stdlib.core_api
import mockito
import sqlalchemy.orm
import sqlalchemy.sql.functions as safunc
from eave.core import EAVE_API_JWT_ISSUER, EAVE_API_SIGNING_KEY
from httpx import AsyncClient, Response
from sqlalchemy import literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class AnyStandardOrm(Protocol):
    id: sqlalchemy.orm.Mapped[UUID]


T = TypeVar("T")
J = TypeVar("J", bound=AnyStandardOrm)

TEST_SIGNING_KEY = eave.stdlib.signing.SigningKeyDetails(
    id="test-key",
    version="1",
    algorithm=eave.stdlib.signing.SigningAlgorithm.RS256,
)

eave.core.internal.database.async_engine.echo = False  # shhh


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    async def asyncSetUp(self) -> None:
        self.testdata: typing.Dict[str, Any] = {}

        self.mock_env = {
            "EAVE_API_BASE": "https://api.eave.dev:8080",
            "EAVE_WWW_BASE": "https://www.eave.dev:8080",
            "EAVE_COOKIE_DOMAIN": ".eave.dev",
            "EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_B64": eave.stdlib.util.b64encode(
                json.dumps(
                    {
                        "web": {
                            "client_id": self.anystring("google_oauth_client_id"),
                            "project_id": "eavefyi-dev",
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "client_secret": self.anystring("google_oauth_client_secret"),
                            "redirect_uris": ["https://api.eave.dev:8080/oauth/google/callback"],
                        }
                    }
                )
            ),
        }

        async with eave.core.internal.database.async_engine.connect() as db_connection:
            await db_connection.run_sync(eave.core.internal.orm.base.get_base_metadata().drop_all)
            await db_connection.commit()
            await db_connection.run_sync(eave.core.internal.orm.base.get_base_metadata().create_all)
            await db_connection.commit()
            # tnames = ",".join([t.name for t in eave.core.internal.orm._get_base_metadata().sorted_tables])
            # await connection.execute(text(f"truncate {tnames}"))

        # transport = httpx.ASGITransport(
        #     app=eave.core.app.app,  # type:ignore
        #     raise_app_exceptions=True,
        # )
        self.httpclient = AsyncClient(
            app=eave.core.app.app,
            base_url=eave.core.internal.app_config.eave_api_base,
        )

        # Tests should never call out to KMS
        self.mock_signing()
        self.mock_google_services()
        self.mock_environment()

    async def asyncTearDown(self) -> None:
        # mockito.verifyStubbedInvocationsAreUsed()
        mockito.unstub()
        await self.httpclient.aclose()
        await eave.core.internal.database.async_engine.dispose()

    @staticmethod
    async def mock_coroutine(value: T) -> T:
        return value

    def unwrap(self, value: Optional[T]) -> T:
        assert value is not None
        return value

    def anystring(self, name: Optional[str] = None) -> str:
        if name is None:
            name = str(uuid4())

        if name not in self.testdata:
            data = str(uuid4())
            self.testdata[name] = data

        value: str = self.testdata[name]
        return value

    def anyuuid(self, name: Optional[str] = None) -> UUID:
        if name is None:
            name = str(uuid4())

        if name not in self.testdata:
            data = uuid4()
            self.testdata[name] = data

        value: UUID = self.testdata[name]
        return value

    def anyint(self, name: Optional[str] = None) -> int:
        if name is None:
            name = str(uuid4())

        if name not in self.testdata:
            data = random.randint(0, 9999)
            self.testdata[name] = data

        value: int = self.testdata[name]
        return value

    @property
    def db_session(self) -> async_sessionmaker[AsyncSession]:
        session: async_sessionmaker[AsyncSession] = eave.core.internal.database.async_session
        return session

    async def save(self, obj: J) -> J:
        async with self.db_session.begin() as db_session:
            db_session.add(obj)
        return obj

    async def reload(self, obj: J) -> J | None:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        async with self.db_session.begin() as db_session:
            result: J | None = await db_session.scalar(stmt)

        return result

    async def delete(self, obj: AnyStandardOrm) -> None:
        async with self.db_session.begin() as db_session:
            await db_session.delete(obj)

    async def count(self, cls: Any) -> int:
        query = select(safunc.count(cls.id))
        async with self.db_session.begin() as db_session:
            count: int | None = await db_session.scalar(query)

        if count is None:
            count = 0
        return count

    async def make_request(
        self,
        path: str,
        payload: Optional[eave.stdlib.util.JsonObject] = None,
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

    def mock_environment(self) -> None:
        def _getenv(key: str) -> str | None:
            if key in self.mock_env:
                return self.mock_env[key]
            else:
                return os.environ[key]

        mockito.when2(os.getenv, ...).thenAnswer(_getenv)

    def mock_google_services(self) -> None:
        def _get_secret(key: str) -> str:
            return self.mock_env.get(key, f"not mocked: {key}")

        def _get_runtimeconfig(key: str) -> str:
            return self.mock_env.get(key, f"not mocked: {key}")

        mockito.when2(f"eave.stdlib.config.EaveConfig.get_secret", ...).thenAnswer(_get_secret)
        mockito.when2(f"eave.stdlib.config.EaveConfig.get_runtimeconfig", ...).thenAnswer(_get_runtimeconfig)

    def mock_signing(self) -> None:
        def _sign_b64(signing_key: eave.stdlib.signing.SigningKeyDetails, data: str | bytes) -> str:
            value: str = eave.stdlib.util.b64encode(eave.stdlib.util.sha256hexdigest(data))
            return value

        def _verify_signature_or_exception(
            signing_key: eave.stdlib.signing.SigningKeyDetails, message: str | bytes, signature: str
        ) -> None:
            if signature != eave.stdlib.util.b64encode(eave.stdlib.util.sha256hexdigest(message)):
                raise eave.stdlib.exceptions.InvalidSignatureError()

        mockito.when2(eave.stdlib.signing.sign_b64, ...).thenAnswer(_sign_b64)
        mockito.when2(eave.stdlib.signing.verify_signature_or_exception, ...).thenAnswer(_verify_signature_or_exception)

    async def mock_auth_token(
        self, account: eave.core.internal.orm.account.AccountOrm
    ) -> Tuple[eave.stdlib.jwt.JWT, eave.stdlib.jwt.JWT, eave.core.internal.orm.auth_token.AuthTokenOrm]:
        before_count = await self.count(eave.core.internal.orm.auth_token.AuthTokenOrm)

        access_token = eave.stdlib.jwt.create_jwt(
            signing_key=EAVE_API_SIGNING_KEY,
            purpose=eave.stdlib.jwt.JWTPurpose.access,
            iss=EAVE_API_JWT_ISSUER,
            aud=eave.stdlib.eave_origins.EaveOrigin.eave_www.value,
            sub=str(account.id),
        )

        refresh_token = eave.stdlib.jwt.create_jwt(
            signing_key=EAVE_API_SIGNING_KEY,
            purpose=eave.stdlib.jwt.JWTPurpose.refresh,
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
            access_token=eave.stdlib.util.sha256hexdigest(access_token.to_str()),
            refresh_token=eave.stdlib.util.sha256hexdigest(refresh_token.to_str()),
            jti=access_token.payload.jti,
            iss=access_token.payload.iss,
            aud=access_token.payload.aud,
            expires=datetime.utcfromtimestamp(float(access_token.payload.exp)),
        )

        auth_token = await self.save(auth_token)
        assert (await self.count(eave.core.internal.orm.auth_token.AuthTokenOrm)) == before_count + 1
        return (access_token, refresh_token, auth_token)

    async def make_team(self) -> eave.core.internal.orm.TeamOrm:
        team = eave.core.internal.orm.TeamOrm(
            name=self.anystring("team name"), document_platform=eave.stdlib.core_api.enums.DocumentPlatform.confluence
        )
        await self.save(team)
        return team

    async def make_account(self, **kwargs: Any) -> eave.core.internal.orm.account.AccountOrm:
        if not (team_id := kwargs.pop("team_id", None)):
            team = await self.make_team()
            team_id = team.id

        account = eave.core.internal.orm.account.AccountOrm(
            auth_provider=kwargs.pop("auth_provider", eave.stdlib.core_api.enums.AuthProvider.slack),
            auth_id=kwargs.pop("auth_id", self.anystring("auth_id")),
            access_token=kwargs.pop("access_token", self.anystring("oauth_token")),
            refresh_token=kwargs.pop("refresh_token", self.anystring("refresh_token")),
            team_id=team_id,
            **kwargs,
        )
        await self.save(account)
        return account

    async def get_eave_account(self, id: UUID) -> eave.core.internal.orm.AccountOrm | None:
        async with self.db_session.begin() as db_session:
            acct = await eave.core.internal.orm.AccountOrm.one_or_none(session=db_session, id=id)

        return acct

    async def get_eave_team(self, id: UUID) -> eave.core.internal.orm.TeamOrm | None:
        async with self.db_session.begin() as db_session:
            acct = await eave.core.internal.orm.TeamOrm.one_or_none(session=db_session, team_id=id)

        return acct
