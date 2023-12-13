import json
import unittest
import unittest.mock
import urllib.parse
import uuid
import pydantic
import sqlalchemy
from typing import Any, Optional, Protocol, TypeVar
from uuid import UUID
from eave.core.internal.oauth.slack import SlackIdentity
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.resource_mutex import ResourceMutexOrm

import eave.stdlib.signing
import eave.stdlib.eave_origins
import eave.stdlib.typing

from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.core_api.models.team import DocumentPlatform
import eave.stdlib.test_util
import eave.stdlib.atlassian
import eave.stdlib.jwt
import eave.stdlib.requests
import sqlalchemy.orm
import sqlalchemy.sql.functions as safunc
from httpx import AsyncClient, Response
from sqlalchemy import literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession

import eave.core.app
import eave.core.internal
import eave.core.internal.oauth.atlassian
import eave.core.internal.orm
import eave.core.internal.orm.base


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


async def _onetime_setup_db() -> None:
    global _DB_SETUP
    if _DB_SETUP:
        return

    print("Running one-time DB setup...")
    async with eave.core.internal.database.async_session() as db_session:
        conn = await db_session.connection()
        await conn.run_sync(eave.core.internal.orm.base.get_base_metadata().drop_all)
        await db_session.commit()

    async with eave.core.internal.database.async_session() as db_session:
        conn = await db_session.connection()
        await conn.run_sync(eave.core.internal.orm.base.get_base_metadata().create_all)
        await db_session.commit()

    _DB_SETUP = True


class BaseTestCase(eave.stdlib.test_util.UtilityBaseTestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        await _onetime_setup_db()
        engine = eave.core.internal.database.async_engine.execution_options(isolation_level="READ COMMITTED")
        self.db_session = eave.core.internal.database.async_sessionmaker(engine, expire_on_commit=False)
        # self.db_session = eave.core.internal.database.async_session

        # transport = httpx.ASGITransport(
        #     app=eave.core.app.app,  # type:ignore
        #     raise_app_exceptions=True,
        # )
        self.httpclient = AsyncClient(
            app=eave.core.app.app,
            base_url=eave.core.internal.app_config.eave_public_api_base,
        )

        self.mock_atlassian_client()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

        async with self.db_session.begin() as s:
            await s.execute(sqlalchemy.delete(ResourceMutexOrm))


    async def cleanup(self) -> None:
        await super().cleanup()

        tnames = ",".join([t.name for t in eave.core.internal.orm.base.get_base_metadata().sorted_tables])
        conn = await self.db_session().connection()
        await conn.execute(text(f"truncate {tnames} cascade").execution_options(autocommit=True))
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

        if e := headers.get("eave-sig-ts"):
            eave_sig_ts = int(e)
        else:
            eave_sig_ts = eave.stdlib.signing.make_sig_ts()
            headers["eave-sig-ts"] = str(eave_sig_ts)

        if team_id:
            assert "eave-team-id" not in headers
            headers["eave-team-id"] = str(team_id)
        else:
            v = headers.get("eave-team-id")
            team_id = uuid.UUID(v) if v else None

        if account_id:
            assert "eave-account-id" not in headers
            headers["eave-account-id"] = str(account_id)
        else:
            v = headers.get("eave-account-id")
            account_id = uuid.UUID(v) if v else None

        if origin:
            assert "eave-origin" not in headers
            headers["eave-origin"] = origin.value
        else:
            if "eave-origin" not in headers:
                origin = eave.stdlib.eave_origins.EaveApp.eave_www
                headers["eave-origin"] = origin

        if request_id:
            assert "eave-request-id" not in headers
            headers["eave-request-id"] = str(request_id)
        elif "eave-request-id" in headers:
            request_id = uuid.UUID(headers["eave-request-id"])
        else:
            request_id = uuid.uuid4()
            headers["eave-request-id"] = str(request_id)

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

        if sign and "eave-signature" not in headers:
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

    async def make_team(self, session: AsyncSession) -> eave.core.internal.orm.TeamOrm:
        team = await eave.core.internal.orm.TeamOrm.create(
            session=session,
            name=self.anystr("team name"),
            document_platform=DocumentPlatform.confluence,
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
    ) -> eave.core.internal.orm.account.AccountOrm:
        if not team_id:
            team = await self.make_team(session=session)
            team_id = team.id

        account = await eave.core.internal.orm.account.AccountOrm.create(
            session=session,
            team_id=team_id,
            visitor_id=self.anyuuid("account.visitor_id"),
            opaque_utm_params=self.anydict("account.opaque_utm_params"),
            auth_provider=auth_provider or AuthProvider.slack,
            auth_id=auth_id or self.anystr("account.auth_id"),
            access_token=access_token or self.anystr("account.oauth_token"),
            refresh_token=refresh_token or self.anystr("account.refresh_token"),
        )

        match account.auth_provider:
            case AuthProvider.slack:
                mock_userinfo = SlackIdentity(
                    response={
                        "slack_user_id": self.anystr("slack.authed_user.id"),
                        "slack_team_id": self.anystr("slack.team.id"),
                        "email": self.anystr("slack.slack_user_email"),
                        "given_name": self.anystr("slack.slack_given_name"),
                    }
                )

                async def _get_userinfo_or_exception(*args: Any, **kwargs: Any) -> SlackIdentity:
                    return mock_userinfo

                self.patch(
                    unittest.mock.patch(
                        "eave.core.internal.oauth.slack.get_userinfo_or_exception", new=_get_userinfo_or_exception
                    )
                )
            case AuthProvider.google:
                pass
            case AuthProvider.github:
                pass
            case AuthProvider.atlassian:
                pass

        return account

    async def get_eave_account(self, session: AsyncSession, /, id: UUID) -> eave.core.internal.orm.AccountOrm | None:
        acct = await eave.core.internal.orm.AccountOrm.one_or_none(
            session=session, params=AccountOrm.QueryParams(id=id)
        )
        return acct

    async def get_eave_team(self, session: AsyncSession, /, id: UUID) -> eave.core.internal.orm.TeamOrm | None:
        acct = await eave.core.internal.orm.TeamOrm.one_or_none(session=session, team_id=id)
        return acct

    def mock_atlassian_client(self) -> None:
        self.testdata["fake_atlassian_resources"] = [
            eave.stdlib.atlassian.AtlassianAvailableResource(
                data={
                    "id": self.anystr("atlassian_cloud_id"),
                    "url": self.anystr("confluence_document_response._links.base"),
                    "avatarUrl": self.anystr("atlassian.resource.avatar"),
                    "name": self.anystr("atlassian.resource.name"),
                    "scopes": [],
                },
            )
        ]

        self.patch(
            name="atlassian.get_available_resources",
            patch=unittest.mock.patch(
                "eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_available_resources",
                side_effect=lambda *args, **kwargs: self.testdata["fake_atlassian_resources"],
            ),
        )

        self.testdata["fake_atlassian_token"] = {
            "access_token": self.anystr("atlassian.access_token"),
            "refresh_token": self.anystr("atlassian.refresh_token"),
            "expires_in": self.anyint("atlassian.expires_in"),
            "scope": self.anystr("atlassian.scope"),
        }

        self.patch(unittest.mock.patch("eave.core.internal.oauth.atlassian.AtlassianOAuthSession.fetch_token"))
        self.patch(
            name="atlassian.get_token",
            patch=unittest.mock.patch(
                "eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_token",
                side_effect=lambda *args, **kwargs: self.testdata["fake_atlassian_token"],
            ),
        )

        self.testdata["fake_confluence_user"] = eave.stdlib.atlassian.ConfluenceUser(
            data={
                "type": "known",
                "accountType": "atlassian",
                "accountId": self.anystr("confluence.account_id"),
                "displayName": self.anystr("confluence.display_name"),
                "email": self.anystr("confluence.email"),
            },
        )

        self.patch(
            name="atlassian.get_userinfo",
            patch=unittest.mock.patch(
                "eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_userinfo",
                side_effect=lambda *args, **kwargs: self.testdata["fake_confluence_user"],
            ),
        )
