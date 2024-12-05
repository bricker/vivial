from datetime import datetime
from uuid import UUID

import sqlalchemy
import sqlalchemy.dialects.postgresql
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.shared.enums import OutingBudget
from eave.core.shared.errors import ValidationError

from .base import Base
from .util import PG_UUID_EXPR


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
    budget: Mapped[str] = mapped_column()
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
        budget: OutingBudget,
        headcount: int,
        account_id: UUID | None = None,
    ) -> "SurveyOrm":
        obj = SurveyOrm(
            visitor_id=visitor_id,
            account_id=account_id,
            start_time=start_time.replace(tzinfo=None),
            search_area_ids=search_area_ids,
            budget=budget,
            headcount=headcount,
        )

        return obj

    @property
    def outing_budget(self) -> OutingBudget:
        return OutingBudget[self.budget]

    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        if self.budget not in OutingBudget:
            errors.append(ValidationError(field="budget"))

        return errors
