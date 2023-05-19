from sqlalchemy import select
from eave.core.internal.orm.resource_mutex import ResourceMutexOrm
from .base import BaseTestCase


class TestResoureMutex(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_acquire(self) -> None:
        async with self.db_session.begin() as s:
            acquired = await ResourceMutexOrm.acquire(session=s, resource_id=self.anyuuid("resource_id"))
            assert acquired

    async def test_not_acquire(self) -> None:
        async with self.db_session.begin() as s:
            await ResourceMutexOrm.acquire(session=s, resource_id=self.anyuuid("resource_id"))

            acquired = await ResourceMutexOrm.acquire(session=s, resource_id=self.anyuuid("resource_id"))
            assert not acquired

    async def test_release(self) -> None:
        async with self.db_session.begin() as s:
            await ResourceMutexOrm.acquire(session=s, resource_id=self.anyuuid("resource_id"))
            assert (await self.count(s, ResourceMutexOrm)) == 1
            await ResourceMutexOrm.release(session=s, resource_id=self.anyuuid("resource_id"))
            assert (await self.count(s, ResourceMutexOrm)) == 0

    async def test_acquire_expiration(self) -> None:
        resource_id = self.anyuuid("resource_id")

        async with self.db_session.begin() as s:
            acquired = await ResourceMutexOrm.acquire(session=s, resource_id=resource_id)
            assert acquired

            assert (await self.count(s, ResourceMutexOrm)) == 1

            sql = select(ResourceMutexOrm).where(ResourceMutexOrm.resource_id == resource_id)
            mutex = await s.scalar(sql)
            assert mutex
            mutex.created = self.anydatetime("mutex.created", offset=-61)
            await s.flush()

            acquired = await ResourceMutexOrm.acquire(session=s, resource_id=resource_id)
            assert acquired
