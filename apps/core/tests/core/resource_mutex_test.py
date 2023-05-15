from sqlalchemy import select
from eave.core.internal.orm.resource_mutex import ResourceMutexOrm
from .base import BaseTestCase


class TestResoureMutex(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_acquire(self) -> None:
        async with self.db_session.begin() as db_session:
            acquired = await ResourceMutexOrm.acquire(session=db_session, resource_id=self.anyuuid("resource_id"))
            assert acquired

    async def test_not_acquire(self) -> None:
        async with self.db_session.begin() as db_session:
            await ResourceMutexOrm.acquire(session=db_session, resource_id=self.anyuuid("resource_id"))

            acquired = await ResourceMutexOrm.acquire(session=db_session, resource_id=self.anyuuid("resource_id"))
            assert not acquired

    async def test_release(self) -> None:
        async with self.db_session.begin() as db_session:
            await ResourceMutexOrm.acquire(session=db_session, resource_id=self.anyuuid("resource_id"))

        assert (await self.count(ResourceMutexOrm)) == 1

        async with self.db_session.begin() as db_session:
            await ResourceMutexOrm.release(session=db_session, resource_id=self.anyuuid("resource_id"))

        assert (await self.count(ResourceMutexOrm)) == 0

    async def test_acquire_expiration(self) -> None:
        resource_id = self.anyuuid("resource_id")

        async with self.db_session.begin() as db_session:
            acquired = await ResourceMutexOrm.acquire(session=db_session, resource_id=resource_id)
            assert acquired

        assert (await self.count(ResourceMutexOrm)) == 1

        async with self.db_session.begin() as db_session:
            sql = select(ResourceMutexOrm).where(ResourceMutexOrm.resource_id == resource_id)
            mutex = await db_session.scalar(sql)
            assert mutex
            mutex.created = self.anydatetime("mutex.created", offset=-61)
            await db_session.flush()

            acquired = await ResourceMutexOrm.acquire(session=db_session, resource_id=resource_id)
            assert acquired
