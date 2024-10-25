from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import UUID_DEFAULT_EXPR


class AccountBookingOrm(Base):
    __tablename__ = "account_bookings"
    __table_args__ = (
        PrimaryKeyConstraint(
            "account_id",
            "booking_id",
            name="account_booking_pivot_pk",
        ),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
            name="account_id_account_booking_fk",
        ),
        ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.id"],
            ondelete="CASCADE",
            name="booking_id_account_booking_fk",
        ),

        # reverse index to facilitate searching for other accounts
        # associated w/ a booking
        Index(
            "account_booking_pivot_reverse_index",
            "booking_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    account_id: Mapped[UUID] = mapped_column()
    booking_id: Mapped[UUID] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        account_id: UUID,
        booking_id: UUID,
    ) -> Self:
        obj = cls(
            account_id=account_id,
            booking_id=booking_id,
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        account_id: UUID | None = None
        booking_id: UUID | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls)

        if params.account_id is not None:
            lookup = lookup.where(cls.account_id == params.account_id)

        if params.booking_id is not None:
            lookup = lookup.where(cls.booking_id == params.booking_id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> Sequence[Self]:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).all()
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, params: QueryParams) -> Self:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, params: QueryParams) -> Self | None:
        lookup = cls._build_query(params=params)
        result = await session.scalar(lookup)
        return result
