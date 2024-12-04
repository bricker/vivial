import hashlib
import hmac
import os
import re
from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, Select, func, select, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.shared.errors import ValidationError
from eave.stdlib.typing import NOT_SET, NotSet

from .base import Base
from .util import PG_UUID_EXPR


class OutingCategoryPreferenceOrm(Base):
    __tablename__ = "outing_category_preferences"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    account_id: Mapped[UUID] = mapped_column()
    category_type: Mapped[Literal["restaurant", "activity"]] = mapped_column()
    category_id: Mapped[UUID] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        account_id: UUID,
        category_type: Literal["restaurant", "activity"],
        category_id: UUID,
    ) -> "OutingCategoryPreferenceOrm":
        obj = OutingCategoryPreferenceOrm(
            account_id=account_id,
            category_type=category_type,
            category_id=category_id,
        )
        return obj

    @classmethod
    def select(cls, *, account_id: UUID | NotSet = NOT_SET) -> Select[tuple[Self]]:
        query = select(cls)

        if account_id is not NOT_SET:
            query = query.where(cls.account_id == account_id)

        return query

    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        if self.category_type not in ["restaurant", "activity"]:
            errors.append(ValidationError(field="category_type"))

        return errors
