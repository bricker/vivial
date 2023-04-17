import json
import unittest
from typing import Optional, Protocol, TypeVar
from uuid import UUID, uuid4

import eave.core.app
import eave.core.internal.orm as orm
import eave.stdlib.core_api.signing as eave_signing
import eave.stdlib.util as eave_util
import mockito
from eave.core.internal.database import get_session
from httpx import AsyncClient, Response
from sqlalchemy import literal_column, select, text
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
    _testdata = dict[str, str]()
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

        self.dbsession = await get_session()
        self.dbsession.begin()
        connection = await self.dbsession.connection()
        await connection.run_sync(orm.Base.metadata.drop_all)
        await connection.run_sync(orm.Base.metadata.create_all)

        self.httpclient = AsyncClient(app=eave.core.app.app, base_url="http://eave.test")

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

        return self._testdata[name]

    async def save(self, obj: T) -> T:
        self.dbsession.add(obj)
        await self.dbsession.commit()
        return obj

    async def reload(self, obj: P) -> P:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        result = (await self.dbsession.scalars(stmt)).one()
        return result

    async def make_request(
        self, url: str, payload: eave_util.JsonObject, method: str = "POST", headers: dict[str, str] = {}
    ) -> Response:
        data = json.dumps(payload)
        team_id = headers.get("eave-team-id")
        headers["eave-signature"] = eave_signing.sign(payload=data, team_id=team_id)

        response = await self.httpclient.request(
            method,
            url,
            headers=headers,
            content=data,
        )

        return response

    # async def _polyfill_db(self) -> None:
    #     raw_connection = await self._dbconnection.get_raw_connection()
    #     driver = raw_connection.driver_connection
    #     assert isinstance(driver, aiosqlite.core.Connection)
    #     # await driver.enable_load_extension(True)
    #     # await driver.load_extension(path="../vendor/uuid.so")

    #     # driver.create_function(
    #     #     name="gen_random_uuid",
    #     #     narg=0,
    #     #     func=lambda: str(uuid4()),
    #     # )

    #     # (lower(hex(randomblob(16))))

    #     # We're using the Postgres native "gen_random_uuid" function for the ID columns,
    #     # which doesn't exist in SQLite.
    #     await driver.create_function(
    #         name="gen_random_uuid",
    #         num_params=0,
    #         func=lambda: uuid4().hex,
    #     )
