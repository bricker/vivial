from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


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

    account_id: Mapped[UUID] = mapped_column()
    booking_id: Mapped[UUID] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        account_id: UUID,
        booking_id: UUID,
    ) -> "AccountBookingOrm":
        obj = AccountBookingOrm(
            account_id=account_id,
            booking_id=booking_id,
        )

        return obj
