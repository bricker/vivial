from datetime import UTC, datetime
from typing import override
from uuid import UUID
from zoneinfo import ZoneInfo

import sqlalchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.orm.account import AccountOrm
from eave.core.orm.util.mixins import GetOneByIdMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import OutingBudgetColumnType
from eave.core.shared.enums import OutingBudget
from eave.core.shared.errors import ValidationError

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class SurveyOrm(Base, TimedEventMixin, GetOneByIdMixin):
    __tablename__ = "surveys"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    visitor_id: Mapped[str | None] = mapped_column()
    search_area_ids: Mapped[list[UUID]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.Uuid,
            dimensions=1,
        ),
    )
    budget: Mapped[OutingBudget] = mapped_column(type_=OutingBudgetColumnType())
    headcount: Mapped[int] = mapped_column()

    account_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL.value)
    )
    account: Mapped[AccountOrm | None] = relationship(lazy="selectin")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        visitor_id: str | None,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        search_area_ids: list[UUID],
        budget: OutingBudget,
        headcount: int,
        account: AccountOrm | None,
    ) -> None:
        self.account = account
        self.visitor_id = visitor_id
        self.start_time_utc = start_time_utc.astimezone(UTC)
        self.timezone = timezone
        self.search_area_ids = search_area_ids
        self.budget = budget
        self.headcount = headcount

        if session:
            session.add(self)

    @override
    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        if len(self.search_area_ids) == 0:
            errors.append(ValidationError(subject="survey", field="search_area_ids"))

        if self.headcount < 1:
            errors.append(ValidationError(subject="survey", field="headcount"))

        return errors
