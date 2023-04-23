import json
import random
import unittest
import urllib.parse
from typing import Any, Optional, Protocol, TypeVar
from uuid import UUID, uuid4

import eave.core.app
import eave.core.internal.orm as eave_orm
import eave.stdlib.signing as eave_signing
import eave.stdlib.util as eave_util
import mockito
from eave.core.internal.config import app_config
from eave.core.internal.database import get_async_session
from httpx import AsyncClient, Response
from sqlalchemy import literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped


class AnyStandardOrm(Protocol):
    id: Mapped[UUID]


T = TypeVar("T")
P = TypeVar("P", bound=AnyStandardOrm)


async def mock_coroutine(value: T) -> T:
    return value


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    # _dbconnection: AsyncConnection
    _testdata = dict[str, Any]()
    httpclient: AsyncClient
    dbsession: AsyncSession

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._testdata.clear()

        # engine = await get_engine()
        # self._dbconnection = await engine.connect().start()

        self.dbsession = get_async_session()
        self.dbsession.begin()
        connection = await self.dbsession.connection()
        assert connection.engine.url.database == "eave-test"
        await connection.run_sync(eave_orm.Base.metadata.drop_all)
        await connection.run_sync(eave_orm.Base.metadata.create_all)

        self.httpclient = AsyncClient(app=eave.core.app.app, base_url=app_config.eave_api_base)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        mockito.verifyStubbedInvocationsAreUsed()
        mockito.unstub()
        # await self._dbconnection.close()
        await self.httpclient.aclose()
        await self.dbsession.close()

    def unwrap(self, value: Optional[T]) -> T:
        self.assertIsNotNone(value)
        assert value is not None
        return value

    def anystring(self, name: str = str(uuid4())) -> str:
        if name not in self._testdata:
            data = str(uuid4())
            self._testdata[name] = data

        value: str = self._testdata[name]
        return value

    def anyuuid(self, name: str = str(uuid4())) -> UUID:
        if name not in self._testdata:
            data = uuid4()
            self._testdata[name] = data

        value: UUID = self._testdata[name]
        return value

    def anyint(self, name: str = str(uuid4())) -> int:
        if name not in self._testdata:
            data = random.randint(0, 9999)
            self._testdata[name] = data

        value: int = self._testdata[name]
        return value

    async def save(self, obj: T) -> T:
        self.dbsession.add(obj)
        await self.dbsession.commit()
        return obj

    async def reload(self, obj: P) -> P:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        result = (await self.dbsession.scalars(stmt)).one()
        return result

    async def make_request(
        self,
        url: str,
        payload: Optional[eave_util.JsonObject] = None,
        method: str = "POST",
        headers: dict[str, str] = {},
        **kwargs: Any
    ) -> Response:
        request_args: dict[str, Any] = {}

        if payload is not None:
            if method == "GET":
                data = urllib.parse.urlencode(query=payload)
                request_args["params"] = data
            else:
                data = json.dumps(payload)
                request_args["content"] = data

            team_id = headers.get("eave-team-id")
            # FIXME
            # headers["eave-signature"] = eave_signing.sign(payload=data, team_id=team_id)

        response = await self.httpclient.request(
            method,
            url,
            headers=headers,
            **request_args,
            **kwargs,
        )

        return response
