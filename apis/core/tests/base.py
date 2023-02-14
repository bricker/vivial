import unittest
from typing import Any, Optional, Protocol, TypeVar
from uuid import UUID, uuid4

import mockito
from httpx import AsyncClient
from sqlalchemy import literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from sqlalchemy.orm import Mapped

import eave.app
import eave.internal.orm as orm
from eave.internal.database import engine, session_factory


class AnyStandardOrm(Protocol):
    id: Mapped[UUID]


T = TypeVar("T")
P = TypeVar("P", bound=AnyStandardOrm)


async def mock_coroutine(value: T) -> T:
    return value


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    _dbconnection: AsyncConnection
    _testdata = dict[str, str]()
    httpclient: AsyncClient
    dbsession: AsyncSession

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._testdata.clear()

        self._dbconnection = await engine.connect().start()
        await self._dbconnection.run_sync(orm.Base.metadata.drop_all)
        await self._dbconnection.run_sync(orm.Base.metadata.create_all)

        self.dbsession = session_factory()
        self.dbsession.begin()

        self.httpclient = AsyncClient(app=eave.app.app, base_url="http://eave.test")

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        mockito.verifyStubbedInvocationsAreUsed()
        mockito.unstub()
        await self._dbconnection.close()
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
