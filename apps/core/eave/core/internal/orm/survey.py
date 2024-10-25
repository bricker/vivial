import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

import sqlalchemy
import sqlalchemy.dialects.postgresql
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.areas.search_region_code import SearchRegionCode
from eave.core.graphql.types.outing import SurveySubmitErrorCode
from eave.stdlib.exceptions import InvalidDataError, StartTimeTooLateError, StartTimeTooSoonError

from .base import Base
from .util import UUID_DEFAULT_EXPR, validate_time_within_bounds_or_exception


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
    visitor_id: Mapped[UUID] = mapped_column()
    account_id: Mapped[UUID | None] = mapped_column()
    start_time: Mapped[datetime] = mapped_column()
    search_area_ids: Mapped[list[str]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.String,
            dimensions=1,
        ),
    )
    budget: Mapped[int] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        visitor_id: UUID,
        start_time: datetime,
        search_area_ids: list[SearchRegionCode],
        budget: int,
        headcount: int,
        account_id: UUID | None = None,
    ) -> Self:
        obj = cls(
            visitor_id=visitor_id,
            account_id=account_id,
            start_time=start_time.replace(tzinfo=None),
            search_area_ids=search_area_ids,
            budget=budget,
            headcount=headcount,
        )

        obj.validate()

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
    async def query(cls, session: AsyncSession, params: QueryParams) -> Sequence[Self]:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).all()
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

    def validate(self) -> None:
        if not len(self.search_area_ids) > 0:
            raise InvalidDataError(code=SurveySubmitErrorCode.ONE_SEARCH_REGION_REQUIRED)
        try:
            validate_time_within_bounds_or_exception(self.start_time)
        except StartTimeTooSoonError:
            raise InvalidDataError(code=SurveySubmitErrorCode.START_TIME_TOO_SOON)
        except StartTimeTooLateError:
            raise InvalidDataError(code=SurveySubmitErrorCode.START_TIME_TOO_LATE)
