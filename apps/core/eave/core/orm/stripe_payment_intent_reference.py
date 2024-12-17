from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.orm.account import AccountOrm

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class StripePaymentIntentReferenceOrm(Base):
    __tablename__ = "stripe_payment_intent_references"
    __table_args__ = (PrimaryKeyConstraint("account_id", "stripe_payment_intent_id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, unique=True)
    stripe_payment_intent_id: Mapped[str] = mapped_column()

    account_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    account: Mapped[AccountOrm] = relationship(lazy="selectin")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        account: AccountOrm,
        stripe_payment_intent_id: str,
    ) -> None:
        self.account = account
        self.stripe_payment_intent_id = stripe_payment_intent_id

        if session:
            session.add(self)

    @classmethod
    async def get_one(cls, session: AsyncSession, *, account_id: UUID, stripe_payment_intent_id: str) -> Self:
        return await session.get_one(cls, (account_id, stripe_payment_intent_id))
