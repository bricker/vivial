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
from sqlalchemy.orm import Mapped, mapped_column, validates

from eave.stdlib.exceptions import ValidationError, StartTimeTooLateError, StartTimeTooSoonError

from .base import Base
from .util import PG_UUID_EXPR, validate_time_within_bounds_or_exception


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

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    visitor_id: Mapped[UUID] = mapped_column()
    account_id: Mapped[UUID | None] = mapped_column()
    start_time: Mapped[datetime] = mapped_column()
    search_area_ids: Mapped[list[UUID]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.Uuid,
            dimensions=1,
        ),
    )
    budget: Mapped[int] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        visitor_id: UUID,
        start_time: datetime,
        search_area_ids: list[UUID],
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

        return obj

    @validates("search_area_ids")
    def validate_search_area_ids(self, key: str, value: list[UUID]) -> list[UUID]:
        if not len(value) > 0:
            raise ValidationError(code=PlanOutingErrorCode.ONE_SEARCH_REGION_REQUIRED)
        return value

    @validates("start_time")
    def validate_start_time(self, key: str, value: datetime) -> datetime:
        try:
            validate_time_within_bounds_or_exception(value)
        except StartTimeTooSoonError:
            raise ValidationError(code=PlanOutingErrorCode.START_TIME_TOO_SOON)
        except StartTimeTooLateError:
            raise ValidationError(code=PlanOutingErrorCode.START_TIME_TOO_LATE)
        return value
