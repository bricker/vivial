from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, Select, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.orm.account import AccountOrm
from eave.core.orm.util.mixins import GetOneByIdMixin
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class StripePaymentIntentReferenceOrm(Base, GetOneByIdMixin):
    __tablename__ = "stripe_payment_intent_references"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    stripe_payment_intent_id: Mapped[str] = mapped_column(index=True)

    account_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE), index=True
    )
    account: Mapped[AccountOrm] = relationship(lazy="selectin")

    def __init__(
        self,
        *,
        account: AccountOrm,
        stripe_payment_intent_id: str,
    ) -> None:
        self.account = account
        self.stripe_payment_intent_id = stripe_payment_intent_id

    @classmethod
    def select(cls, *, stripe_payment_intent_id: str = NOT_SET) -> Select[tuple[Self]]:
        query = select(cls)

        if stripe_payment_intent_id is not NOT_SET:
            query = query.where(cls.stripe_payment_intent_id == stripe_payment_intent_id)

        return query
