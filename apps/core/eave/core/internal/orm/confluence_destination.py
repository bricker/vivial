from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID
import uuid

from sqlalchemy import ForeignKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.team import ConfluenceDestination

from .base import Base
from .util import UUID_DEFAULT_EXPR


class ConfluenceDestinationOrm(Base):
    __tablename__ = "confluence_destinations"
    __table_args__ = (
        ForeignKeyConstraint(["connect_installation_id"], ["connect_installations.id"], ondelete="CASCADE"),
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR, primary_key=True)
    connect_installation_id: Mapped[uuid.UUID] = mapped_column()
    space_key: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @property
    def api_model(self) -> ConfluenceDestination:
        return ConfluenceDestination.from_orm(self)

    @classmethod
    async def create(cls, session: AsyncSession, connect_installation_id: UUID, space_key: str) -> Self:
        obj = cls(
            connect_installation_id=connect_installation_id,
            space_key=space_key,
        )
        session.add(obj)
        await session.flush()
        return obj

    class QueryParams(TypedDict):
        id: NotRequired[uuid.UUID]
        connect_installation_id: NotRequired[uuid.UUID]

    @classmethod
    def query(cls, **kwargs: Unpack[QueryParams]) -> Select[Tuple[Self]]:
        id = kwargs.get("id")
        connect_installation_id = kwargs.get("connect_installation_id")
        assert id or connect_installation_id, "At least one of id or connect_installation_id is required"

        lookup = select(cls)

        if id:
            lookup = lookup.where(cls.id == id)

        if connect_installation_id:
            lookup = lookup.where(cls.connect_installation_id == connect_installation_id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self:
        lookup = cls.query(**kwargs).limit(1)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self | None:
        lookup = cls.query(**kwargs).limit(1)
        result = await session.scalar(lookup)
        return result
