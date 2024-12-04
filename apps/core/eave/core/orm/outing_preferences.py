import hashlib
import hmac
import os
import re
from datetime import datetime
from typing import Literal, Self
from uuid import UUID
import strawberry

from sqlalchemy import PrimaryKeyConstraint, Select, func, select, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.shared.errors import ValidationError
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util import PG_UUID_EXPR


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
    open_to_bars: Mapped[bool | None] = mapped_column()
    activity_category_ids: Mapped[list[UUID] | None] = mapped_column()
    restaurant_category_ids: Mapped[list[UUID] | None] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        account_id: UUID,
        open_to_bars: bool | None,
        activity_category_ids: list[UUID] | None,
        restaurant_category_ids: list[UUID] | None,
    ) -> "OutingPreferencesOrm":
        obj = OutingPreferencesOrm(
            account_id=account_id,
            open_to_bars=open_to_bars,
            activity_category_ids=activity_category_ids,
            restaurant_category_ids=restaurant_category_ids,
        )
        return obj

    def update(self, *, open_to_bars: bool = strawberry.UNSET, restaurant_category_ids: list[UUID] = strawberry.UNSET, activity_category_ids: list[UUID] = strawberry.UNSET) -> Self:
        if open_to_bars is not strawberry.UNSET:
            self.open_to_bars = open_to_bars

        if restaurant_category_ids is not strawberry.UNSET:
            self.restaurant_category_ids = restaurant_category_ids

        if activity_category_ids is not strawberry.UNSET:
            self.activity_category_ids = activity_category_ids

        return self

    @classmethod
    def select(cls, *, account_id: UUID = NOT_SET) -> Select[tuple[Self]]:
        query = select(cls)

        if account_id is not NOT_SET:
            query = query.where(cls.account_id == account_id)

        return query
