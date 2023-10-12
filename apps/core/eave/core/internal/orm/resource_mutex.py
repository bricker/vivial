from datetime import datetime, timedelta
from typing import Literal, Optional
from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.logging import eaveLogger

from .base import Base
from .util import UUID_DEFAULT_EXPR, current_timestamp_utc


class ResourceMutexOrm(Base):
    __tablename__ = "resource_mutexes"

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR, primary_key=True)
    resource_id: Mapped[UUID] = mapped_column(unique=True)
    created: Mapped[datetime] = mapped_column(server_default=current_timestamp_utc())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=current_timestamp_utc())

    @classmethod
    async def acquire(cls, session: AsyncSession, resource_id: UUID) -> bool:
        query = select(cls).where(cls.resource_id == resource_id)
        result = await session.scalar(query)

        if result:
            # A lock already exists for this resource.
            # Automatically release locks after 60 seconds
            if datetime.utcnow() >= (result.created + timedelta(seconds=60)):
                eaveLogger.warning("A lock is being forcefully released")
                await cls.release(session=session, resource_id=resource_id)
            else:
                # The lock is valid; access is denied.
                return False

        obj = cls(resource_id=resource_id)
        session.add(obj)
        try:
            await session.flush()
            return True
        except Exception:
            eaveLogger.exception("Error while acquiring lock")
            return False

    @classmethod
    async def release(cls, session: AsyncSession, resource_id: UUID) -> Literal[True]:
        sql = delete(cls).where(cls.resource_id == resource_id)
        await session.execute(sql)
        return True
