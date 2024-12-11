from typing import Self
from uuid import UUID

import sqlalchemy.dialects.postgresql
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, Select, select
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.account import AccountOrm
from eave.core.orm.util.mixins import GetOneByIdMixin
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class OutingPreferencesOrm(Base, GetOneByIdMixin):
    __tablename__ = "outing_preferences"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE)
    )

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

    def __init__(
        self,
        *,
        account_id: UUID,
        activity_category_ids: list[UUID] | None,
        restaurant_category_ids: list[UUID] | None,
    ) -> None:
        self.account_id = account_id
        self.activity_category_ids = activity_category_ids
        self.restaurant_category_ids = restaurant_category_ids

    @classmethod
    def select(cls, *, account_id: UUID = NOT_SET) -> Select[tuple[Self]]:
        query = select(cls)

        if account_id is not NOT_SET:
            query = query.where(cls.account_id == account_id)

        return query
