import json
import unittest
import unittest.mock
import urllib.parse
import uuid
from typing import Any, Optional, Protocol, TypeVar
from uuid import UUID

import eave.stdlib
import eave.stdlib.test_util
import eave.stdlib.atlassian
import eave.stdlib.core_api
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
            base_url=eave.core.internal.app_config.eave_api_base,
        )

        self.mock_atlassian_client()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

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
        payload: Optional[eave.stdlib.typing.JsonObject] = None,
        method: str = "POST",
        headers: Optional[dict[str, Optional[str]]] = None,
        origin: Optional[eave.stdlib.eave_origins.EaveOrigin] = None,
        team_id: Optional[uuid.UUID] = None,
        account_id: Optional[uuid.UUID] = None,
        access_token: Optional[str] = None,
        request_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> Response:
        if headers is None:
            headers = {}

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
                origin = eave.stdlib.EaveOrigin.eave_www
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
        encoded_payload = json.dumps(payload) if payload else ""

        if method == "GET":
            data = urllib.parse.urlencode(query=payload or {})
            request_args["params"] = data
        else:
            request_args["content"] = encoded_payload

        if "eave-signature" not in headers:
            origin = origin or eave.stdlib.EaveOrigin.eave_www
            signature_message = eave.stdlib.requests.build_message_to_sign(
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

    async def make_team(self, session: AsyncSession) -> eave.core.internal.orm.TeamOrm:
        team = await eave.core.internal.orm.TeamOrm.create(
            session=session,
            name=self.anystring("team name"),
            document_platform=eave.stdlib.core_api.enums.DocumentPlatform.confluence,
            beta_whitelisted=False,
        )

        return team

    async def make_account(
        self,
        session: AsyncSession,
        /,
        team_id: Optional[uuid.UUID] = None,
        auth_provider: Optional[eave.stdlib.core_api.enums.AuthProvider] = None,
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
            auth_provider=auth_provider or eave.stdlib.core_api.enums.AuthProvider.slack,
            auth_id=auth_id or self.anystring("account.auth_id"),
            access_token=access_token or self.anystring("account.oauth_token"),
            refresh_token=refresh_token or self.anystring("account.refresh_token"),
        )

        return account

    async def get_eave_account(self, session: AsyncSession, /, id: UUID) -> eave.core.internal.orm.AccountOrm | None:
        acct = await eave.core.internal.orm.AccountOrm.one_or_none(session=session, id=id)
        return acct

    async def get_eave_team(self, session: AsyncSession, /, id: UUID) -> eave.core.internal.orm.TeamOrm | None:
        acct = await eave.core.internal.orm.TeamOrm.one_or_none(session=session, team_id=id)
        return acct

    def mock_atlassian_client(self) -> None:
        self.patch(name="AtlassianRestAPI.get", patch=unittest.mock.patch("atlassian.rest_client.AtlassianRestAPI.get"))
        self.patch(name="AtlassianRestAPI.delete", patch=unittest.mock.patch("atlassian.rest_client.AtlassianRestAPI.delete"))

        self.testdata["fake_atlassian_resources"] = [
            eave.stdlib.atlassian.AtlassianAvailableResource(
                id=self.anystring("atlassian_cloud_id"),
                url=self.anystring("confluence_document_response._links.base"),
                avatarUrl=self.anystring("atlassian.resource.avatar"),
                name=self.anystring("atlassian.resource.name"),
                scopes=[],
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
            "access_token": self.anystring("atlassian.access_token"),
            "refresh_token": self.anystring("atlassian.refresh_token"),
            "expires_in": self.anyint("atlassian.expires_in"),
            "scope": self.anystring("atlassian.scope"),
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
                "accountId": self.anystring("confluence.account_id"),
                "displayName": self.anystring("confluence.display_name"),
                "email": self.anystring("confluence.email"),
            },
        )

        self.patch(
            name="atlassian.get_userinfo",
            patch=unittest.mock.patch(
                "eave.core.internal.oauth.atlassian.AtlassianOAuthSession.get_userinfo",
                side_effect=lambda *args, **kwargs: self.testdata["fake_confluence_user"],
            ),
        )

    def confluence_document_response_fixture(self) -> eave.stdlib.typing.JsonObject:
        return {
            "id": self.anystring("confluence_document_response.id"),
            "type": "page",
            "status": "current",
            "title": self.anystring("confluence_document_response.title"),
            "space": {
                "id": 229380,
                "key": "EAVE",
                "name": "Eave",
                "type": "global",
                "status": "current",
                "_expandable": {
                    "settings": "/rest/api/space/EAVE/settings",
                    "metadata": "",
                    "operations": "",
                    "lookAndFeel": "/rest/api/settings/lookandfeel?spaceKey=EAVE",
                    "identifiers": "",
                    "permissions": "",
                    "icon": "",
                    "description": "",
                    "theme": "/rest/api/space/EAVE/theme",
                    "history": "",
                    "homepage": "/rest/api/content/229464",
                },
                "_links": {"webui": "/spaces/EAVE", "self": "https://eave-fyi.atlassian.net/wiki/rest/api/space/EAVE"},
            },
            "history": {
                "latest": True,
                "createdBy": {
                    "type": "known",
                    "accountId": "63a5faccb790087ed70fc684",
                    "accountType": "atlassian",
                    "email": "bryan@eave.fyi",
                    "publicName": "Bryan Ricker",
                    "profilePicture": {
                        "path": "/wiki/aa-avatar/63a5faccb790087ed70fc684",
                        "width": 48,
                        "height": 48,
                        "isDefault": False,
                    },
                    "displayName": "Bryan Ricker",
                    "isExternalCollaborator": False,
                    "_expandable": {"operations": "", "personalSpace": ""},
                    "_links": {
                        "self": "https://eave-fyi.atlassian.net/wiki/rest/api/user?accountId=63a5faccb790087ed70fc684"
                    },
                },
                "createdDate": "2023-01-08T23:36:45.274Z",
                "_expandable": {
                    "lastUpdated": "",
                    "previousVersion": "",
                    "contributors": "",
                    "nextVersion": "",
                    "ownedBy": "",
                },
                "_links": {"self": "https://eave-fyi.atlassian.net/wiki/rest/api/content/3375127/history"},
            },
            "version": {
                "by": {
                    "type": "known",
                    "accountId": "63a5faccb790087ed70fc684",
                    "accountType": "atlassian",
                    "email": "bryan@eave.fyi",
                    "publicName": "Bryan Ricker",
                    "profilePicture": {
                        "path": "/wiki/aa-avatar/63a5faccb790087ed70fc684",
                        "width": 48,
                        "height": 48,
                        "isDefault": False,
                    },
                    "displayName": "Bryan Ricker",
                    "isExternalCollaborator": False,
                    "_expandable": {"operations": "", "personalSpace": ""},
                    "_links": {
                        "self": "https://eave-fyi.atlassian.net/wiki/rest/api/user?accountId=63a5faccb790087ed70fc684"
                    },
                },
                "when": "2023-01-08T23:36:45.274Z",
                "friendlyWhen": "just a moment ago",
                "message": "",
                "number": 1,
                "minorEdit": False,
                "confRev": "confluence$content$3375127.2",
                "contentTypeModified": False,
                "_expandable": {"collaborators": "", "content": "/rest/api/content/3375127"},
                "_links": {"self": "https://eave-fyi.atlassian.net/wiki/rest/api/content/3375127/version/1"},
            },
            "ancestors": [
                {
                    "id": "229464",
                    "type": "page",
                    "status": "current",
                    "title": "Eave",
                    "macroRenderedOutput": {},
                    "extensions": {"position": 655},
                    "_expandable": {
                        "container": "/rest/api/space/EAVE",
                        "metadata": "",
                        "restrictions": "/rest/api/content/229464/restriction/byOperation",
                        "history": "/rest/api/content/229464/history",
                        "body": "",
                        "version": "",
                        "descendants": "/rest/api/content/229464/descendant",
                        "space": "/rest/api/space/EAVE",
                        "childTypes": "",
                        "schedulePublishInfo": "",
                        "operations": "",
                        "schedulePublishDate": "",
                        "children": "/rest/api/content/229464/child",
                        "ancestors": "",
                    },
                    "_links": {
                        "self": "https://eave-fyi.atlassian.net/wiki/rest/api/content/229464",
                        "tinyui": "/x/WIAD",
                        "editui": "/pages/resumedraft.action?draftId=229464",
                        "webui": "/spaces/EAVE/overview",
                    },
                }
            ],
            "container": {
                "id": 229380,
                "key": "EAVE",
                "name": "Eave",
                "type": "global",
                "status": "current",
                "history": {
                    "createdBy": {
                        "type": "known",
                        "accountId": "63a5faccb790087ed70fc684",
                        "accountType": "atlassian",
                        "email": "bryan@eave.fyi",
                        "publicName": "Bryan Ricker",
                        "profilePicture": {
                            "path": "/wiki/aa-avatar/63a5faccb790087ed70fc684",
                            "width": 48,
                            "height": 48,
                            "isDefault": False,
                        },
                        "displayName": "Bryan Ricker",
                        "isExternalCollaborator": False,
                        "_expandable": {"operations": "", "personalSpace": ""},
                        "_links": {
                            "self": "https://eave-fyi.atlassian.net/wiki/rest/api/user?accountId=63a5faccb790087ed70fc684"
                        },
                    },
                    "createdDate": "2022-12-23T19:06:29.653Z",
                },
                "_expandable": {
                    "settings": "/rest/api/space/EAVE/settings",
                    "metadata": "",
                    "operations": "",
                    "lookAndFeel": "/rest/api/settings/lookandfeel?spaceKey=EAVE",
                    "identifiers": "",
                    "permissions": "",
                    "icon": "",
                    "description": "",
                    "theme": "/rest/api/space/EAVE/theme",
                    "homepage": "/rest/api/content/229464",
                },
                "_links": {"webui": "/spaces/EAVE", "self": "https://eave-fyi.atlassian.net/wiki/rest/api/space/EAVE"},
            },
            "macroRenderedOutput": {},
            "body": {
                "storage": {
                    "value": "<h1>Test Body</h1>\\n\\n<p>Hello</p>\\n\\n<h3>Smaller Header</h3>\\n\\n<p>OK</p>",
                    "representation": "storage",
                    "embeddedContent": [],
                    "_expandable": {"content": "/rest/api/content/3375127"},
                },
                "_expandable": {
                    "editor": "",
                    "atlas_doc_format": "",
                    "view": "",
                    "export_view": "",
                    "styled_view": "",
                    "dynamic": "",
                    "editor2": "",
                    "anonymous_export_view": "",
                },
            },
            "extensions": {"position": 939968483},
            "_expandable": {
                "childTypes": "",
                "schedulePublishInfo": "",
                "metadata": "",
                "operations": "",
                "schedulePublishDate": "",
                "children": "/rest/api/content/3375127/child",
                "restrictions": "/rest/api/content/3375127/restriction/byOperation",
                "descendants": "/rest/api/content/3375127/descendant",
            },
            "_links": {
                "editui": "/pages/resumedraft.action?draftId=3375127",
                "webui": "/spaces/EAVE/pages/3375127/Test+Title+917c1747-5d52-421e-aaf6-05ad519d5dd8",
                "context": "/wiki",
                "self": "https://eave-fyi.atlassian.net/wiki/rest/api/content/3375127",
                "tinyui": "/" + self.anystring("confluence_document_response._links.tinyui"),
                "collection": "/rest/api/content",
                "base": f"{self.anystring('confluence_document_response._links.base')}/wiki",
            },
        }

    def slack_chat_postMessage_response_fixture(self) -> eave.stdlib.typing.JsonObject:
        return {
            "ok": True,
            "channel": self.anystring("slack.channel"),
            "ts": self.anystring("slack.ts"),
            "message": {
                "text": self.anystring("slack.message.text"),
                "username": self.anystring("slack.message.username"),
                "bot_id": self.anystring("slack.message.bot_id"),
                "attachments": [
                    {
                        "text": self.anystring("slack.message.attachments[0].text"),
                        "id": self.anyint("slack.message.attachments[0].id"),
                        "fallback": self.anystring("slack.message.attachments[0].fallback"),
                    }
                ],
                "type": "message",
                "subtype": "bot_message",
                "ts": self.anystring("slack.ts"),
            },
        }
