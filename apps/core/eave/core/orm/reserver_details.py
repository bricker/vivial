import re
from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, validates

from eave.stdlib.exceptions import ValidationError

from .base import Base
from .util import PG_UUID_EXPR


class ReserverDetailsOrm(Base):
    __tablename__ = "reserver_details"
    __table_args__ = (
        PrimaryKeyConstraint("account_id", "id", name="account_id_id_pk"),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
            name="account_id_reserver_details_fk",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, unique=True)
    account_id: Mapped[UUID] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        account_id: UUID,
        first_name: str,
        last_name: str,
        phone_number: str,
    ) -> Self:
        obj = cls(
            account_id=account_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )

        return obj

    @validates("phone_number")
    def validate_phone_number(self, key: str, value: str) -> str:
        phone_number_pattern = r"^\+?1?\d{10}$"  # TODO: something better
        if re.match(phone_number_pattern, value) is None:
            raise ValidationError(code=SubmitReserverDetailsErrorCode.INVALID_PHONE_NUMBER)
        return value
