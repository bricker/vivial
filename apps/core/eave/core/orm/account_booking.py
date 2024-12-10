from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
from eave.core.orm.util.constants import OnDeleteOption

from .base import Base


class AccountBookingOrm(Base):
    __tablename__ = "account_bookings"
    __table_args__ = (
        PrimaryKeyConstraint(
            "account_id",
            "booking_id",
            name="account_booking_pivot_pk",
        ),
    )

    account_id: Mapped[UUID] = mapped_column(ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    booking_id: Mapped[UUID] = mapped_column(ForeignKey(f"{BookingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE), index=True)

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
