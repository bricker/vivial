from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.activity import ActivityOrm
from eave.core.orm.util.mixins import GetOneByIdMixin

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class TicketTypeOrm(Base, GetOneByIdMixin):
    __tablename__ = "ticket_types"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            columns=["activity_id"],
            refcolumns=["activities.id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    activity_id: Mapped[UUID] = mapped_column(ForeignKey(f"{ActivityOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    base_cost_cents: Mapped[int] = mapped_column()
    service_fee_cents: Mapped[int] = mapped_column()
    tax_percentage: Mapped[float] = mapped_column()
