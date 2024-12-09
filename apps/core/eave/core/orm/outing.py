from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util.constants import PG_UUID_EXPR


class OutingOrm(Base):
    __tablename__ = "outings"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["survey_id"],
            ["surveys.id"],
            ondelete="CASCADE",
            name="survey_id_outing_fk",
        ),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
            name="account_id_outing_fk",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    visitor_id: Mapped[UUID] = mapped_column()
    account_id: Mapped[UUID | None] = mapped_column()
    survey_id: Mapped[UUID] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        visitor_id: UUID,
        survey_id: UUID,
        account_id: UUID | None = None,
    ) -> "OutingOrm":
        obj = OutingOrm(
            visitor_id=visitor_id,
            account_id=account_id,
            survey_id=survey_id,
        )

        return obj
