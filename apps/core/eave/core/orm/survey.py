from datetime import UTC, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

import sqlalchemy
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.util.mixins import TimedEventMixin
from eave.core.orm.util.user_defined_column_types import OutingBudgetColumnType, ZoneInfoColumnType
from eave.core.shared.enums import OutingBudget
from eave.core.shared.errors import ValidationError

from .base import Base
from .util.constants import PG_UUID_EXPR


class SurveyOrm(Base, TimedEventMixin):
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
    search_area_ids: Mapped[list[UUID]] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.Uuid,
            dimensions=1,
        ),
    )
    budget: Mapped[OutingBudget] = mapped_column(type_=OutingBudgetColumnType())
    headcount: Mapped[int] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        visitor_id: UUID,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        search_area_ids: list[UUID],
        budget: OutingBudget,
        headcount: int,
        account_id: UUID | None = None,
    ) -> "SurveyOrm":
        obj = SurveyOrm(
            visitor_id=visitor_id,
            account_id=account_id,
            start_time_utc=start_time_utc.astimezone(UTC),
            timezone=timezone,
            search_area_ids=search_area_ids,
            budget=budget,
            headcount=headcount,
        )

        return obj
