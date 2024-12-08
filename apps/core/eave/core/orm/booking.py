from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util.constants import PG_UUID_EXPR


class BookingOrm(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["reserver_details_id"],
            ["reserver_details.id"],
            ondelete="CASCADE",
            name="reserver_details_booking_fk",
        ),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
            name="accounts_booking_fk",
        ),
        Index(
            "account_id_booking_index",
            "account_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    account_id: Mapped[UUID] = mapped_column()
    reserver_details_id: Mapped[UUID] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        account_id: UUID,
        reserver_details_id: UUID,
    ) -> "BookingOrm":
        obj = BookingOrm(
            account_id=account_id,
            reserver_details_id=reserver_details_id,
        )

        return obj
