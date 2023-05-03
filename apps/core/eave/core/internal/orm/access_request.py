from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Index, PrimaryKeyConstraint, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

from .util import UUID_DEFAULT_EXPR


class AccessRequestOrm(Base):
    __tablename__ = "access_requests"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        Index(None, "visitor_id"),
        Index(None, "email", unique=True),
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    visitor_id: Mapped[Optional[UUID]] = mapped_column()
    email: Mapped[str] = mapped_column()
    opaque_input: Mapped[Optional[str]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())

    @classmethod
    async def one_or_none(cls, session: AsyncSession, email: str) -> Optional["AccessRequestOrm"]:
        statement = select(cls).where(cls.email == email).limit(1)

        access_request = await session.scalar(statement)
        return access_request
