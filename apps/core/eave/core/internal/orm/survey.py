import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from eave.stdlib.core_api.models.search_region import SearchRegionCode
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import UUID_DEFAULT_EXPR


class SurveyOrm(Base):
    __tablename__ = "surveys"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
            name="account_id_survey_fk",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    visitor_id: Mapped[str] = mapped_column()
    account_id: Mapped[UUID | None] = mapped_column()
    start_time: Mapped[datetime] = mapped_column()
    search_area_ids: Mapped[list[str]] = mapped_column()
    budget: Mapped[int] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        visitor_id: str,
        start_time: datetime,
        search_area_ids: list[str],
        budget: int,
        headcount: int,
        account_id: UUID | None = None,
    ) -> Self:
        obj = cls(
            visitor_id=visitor_id,
            account_id=account_id,
            start_time=start_time,
            search_area_ids=search_area_ids,
            budget=budget,
            headcount=headcount,
        )

        if not obj.validate():
            raise Exception("Survey data invalid")

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        id: uuid.UUID | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls).limit(1)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> Self:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, params: QueryParams) -> Self:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, params: QueryParams) -> Self | None:
        lookup = cls._build_query(params=params)
        result = await session.scalar(lookup)
        return result

    def validate(self) -> bool:
        return all(SearchRegionCode.from_str(code) is not None for code in self.search_area_ids)
