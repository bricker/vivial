import eave.stdlib.test_util
import eave.stdlib.requests
import eave.core.internal.orm
import eave.core.internal.orm.base
import eave.core.internal.database
from typing import TypeVar, Optional, Any, Protocol
import uuid
import json
import aiohttp
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import sqlalchemy.orm


class AnyStandardOrm(Protocol):
    id: sqlalchemy.orm.Mapped[uuid.UUID]


T = TypeVar("T")
J = TypeVar("J", bound=AnyStandardOrm)


async def mock_coroutine(value: T) -> T:
    return value


class BaseTestCase(eave.stdlib.test_util.UtilityBaseTestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with eave.core.internal.database.async_engine.connect() as db_connection:
            await db_connection.run_sync(eave.core.internal.orm.base.get_base_metadata().drop_all)
            await db_connection.commit()
            await db_connection.run_sync(eave.core.internal.orm.base.get_base_metadata().create_all)
            await db_connection.commit()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        await eave.core.internal.database.async_engine.dispose()

    async def make_request(
        self,
        path: str,
        payload: Optional[eave.stdlib.typing.JsonObject] = None,
        method: str = "POST",
        base: Optional[str] = None,
        headers: Optional[dict[str, Optional[str]]] = None,
        origin: Optional[eave.stdlib.eave_origins.EaveOrigin] = None,
        team_id: Optional[uuid.UUID] = None,
        account_id: Optional[uuid.UUID] = None,
        access_token: Optional[str] = None,
        request_id: Optional[uuid.UUID] = None,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
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
                url=eave.stdlib.requests.makeurl(path, base),
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

        async with aiohttp.ClientSession() as session:
            response = await session.request(
                method,
                path,
                headers=clean_headers,
                **request_args,
                **kwargs,
            )

            return response

    async def make_team(self) -> eave.core.internal.orm.TeamOrm:
        team = eave.core.internal.orm.TeamOrm(
            name=self.anystring("team name"), document_platform=eave.stdlib.core_api.enums.DocumentPlatform.confluence
        )

        await self.save(team)
        return team

    async def save(self, obj: J) -> J:
        async with self.db_session.begin() as db_session:
            db_session.add(obj)
        return obj

    @property
    def db_session(self) -> async_sessionmaker[AsyncSession]:
        session: async_sessionmaker[AsyncSession] = eave.core.internal.database.async_session
        return session