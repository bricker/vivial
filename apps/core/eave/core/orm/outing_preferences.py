from datetime import datetime
from typing import Self
from uuid import UUID

import sqlalchemy.dialects.postgresql
import strawberry
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR


class OutingPreferencesOrm(Base):
    __tablename__ = "outing_preferences"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    account_id: Mapped[UUID] = mapped_column(unique=True)
    activity_category_ids: Mapped[list[UUID] | None] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.Uuid,
            dimensions=1,
        )
    )
    restaurant_category_ids: Mapped[list[UUID] | None] = mapped_column(
        type_=sqlalchemy.dialects.postgresql.ARRAY(
            item_type=sqlalchemy.types.Uuid,
            dimensions=1,
        )
    )
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        account_id: UUID,
        activity_category_ids: list[UUID] | None,
        restaurant_category_ids: list[UUID] | None,
    ) -> "OutingPreferencesOrm":
        obj = OutingPreferencesOrm(
            account_id=account_id,
            activity_category_ids=activity_category_ids,
            restaurant_category_ids=restaurant_category_ids,
        )
        return obj

    @classmethod
    def select(cls, *, account_id: UUID = NOT_SET) -> Select[tuple[Self]]:
        query = select(cls)

        if account_id is not NOT_SET:
            query = query.where(cls.account_id == account_id)

        return query
