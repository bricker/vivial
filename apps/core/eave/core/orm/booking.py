from typing import TYPE_CHECKING, Self
from uuid import UUID

from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Index, PrimaryKeyConstraint, Select, Table, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.orm.account import AccountOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.orm.util.mixins import GetOneByIdMixin
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption

if TYPE_CHECKING:
    from eave.core.orm.booking_activities_template import BookingActivityTemplateOrm
    from eave.core.orm.booking_reservations_template import BookingReservationTemplateOrm

_account_bookings_join_table = Table(
    "account_bookings",
    Base.metadata,
    Column("booking_id", ForeignKey("bookings.id", ondelete=OnDeleteOption.CASCADE)),
    Column("account_id", ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE)),
)

class BookingOrm(Base, GetOneByIdMixin):
    __tablename__ = "bookings"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)

    stripe_payment_intent_reference_id: Mapped[UUID] = mapped_column(ForeignKey(f"{StripePaymentIntentReferenceOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL), index=True)
    stripe_payment_intent_reference: Mapped[UUID] = mapped_column(lazy="selectin")

    reserver_details_id: Mapped[UUID] = mapped_column(ForeignKey(f"{ReserverDetailsOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL), index=True)
    reserver_details: Mapped[ReserverDetailsOrm] = relationship(lazy="selectin")

    accounts: Mapped[list[AccountOrm]] = relationship(secondary=_account_bookings_join_table, lazy="selectin")

    activities: Mapped[list[BookingActivityTemplateOrm]] = relationship(lazy="selectin")
    reservations: Mapped[list[BookingReservationTemplateOrm]] = relationship(lazy="selectin")

    @classmethod
    def build(
        cls,
        *,
        reserver_details_id: UUID,
        stripe_payment_intent_reference_id: UUID,
    ) -> "BookingOrm":
        obj = BookingOrm(
            reserver_details_id=reserver_details_id,
            stripe_payment_intent_reference_id=stripe_payment_intent_reference_id,
        )

        return obj
