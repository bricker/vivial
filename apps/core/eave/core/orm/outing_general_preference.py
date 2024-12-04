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


class OutingGeneralPreferenceOrm(Base):
    __tablename__ = "outing_general_preferences"
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
    requires_wheelchair_accessibility: Mapped[bool | None] = mapped_column()
    open_to_bars: Mapped[bool | None] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        account_id: UUID,
        requires_wheelchair_accessibility: bool | None = None,
        open_to_bars: bool | None = None,
    ) -> "OutingGeneralPreferenceOrm":
        obj = OutingGeneralPreferenceOrm(
            account_id=account_id,
            requires_wheelchair_accessibility=requires_wheelchair_accessibility,
            open_to_bars=open_to_bars,
        )
        return obj

    @classmethod
    def select(cls, *, account_id: UUID | NotSet = NOT_SET) -> Select[tuple[Self]]:
        query = select(cls)

        if account_id is not NOT_SET:
            query = query.where(cls.account_id == account_id)

        return query
