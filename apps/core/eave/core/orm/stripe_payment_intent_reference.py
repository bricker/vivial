import re
from typing import Self, Tuple
from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, Select, select
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.util.mixins import GetOneByIdMixin
from eave.core.shared.errors import ValidationError
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class StripePaymentIntentReferenceOrm(Base, GetOneByIdMixin):
    __tablename__ = "stripe_payment_intent_references"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    stripe_payment_intent_id: Mapped[str] = mapped_column(index=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE), index=True)
    outing_id: Mapped[UUID | None] = mapped_column(ForeignKey(f"{OutingOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL), index=True)

    def __init__(
        self,
        *,
        account_id: UUID,
        stripe_payment_intent_id: str,
        outing_id: UUID,
    ) -> None:
        self.account_id = account_id
        self.stripe_payment_intent_id = stripe_payment_intent_id
        self.outing_id = outing_id

    @classmethod
    def select(cls, *, stripe_payment_intent_id: str = NOT_SET, outing_id: UUID = NOT_SET) -> Select[Tuple[Self]]:
        query = select(cls)

        if stripe_payment_intent_id is not NOT_SET:
            query = query.where(cls.stripe_payment_intent_id == stripe_payment_intent_id)

        if outing_id is not NOT_SET:
            query = query.where(cls.outing_id == outing_id)

        return query
