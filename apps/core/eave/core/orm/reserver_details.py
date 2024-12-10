import re
from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.account import AccountOrm
from eave.core.orm.util.mixins import GetOneByIdMixin
from eave.core.shared.errors import ValidationError

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class ReserverDetailsOrm(Base, GetOneByIdMixin):
    __tablename__ = "reserver_details"
    __table_args__ = (
        PrimaryKeyConstraint("account_id", "id", name="account_id_id_pk"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, unique=True)
    account_id: Mapped[UUID] = mapped_column(ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        account_id: UUID,
        first_name: str,
        last_name: str,
        phone_number: str,
    ) -> "ReserverDetailsOrm":
        obj = ReserverDetailsOrm(
            account_id=account_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )

        return obj

    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        phone_number_pattern = (
            r"^(\+?1)?[\s-]?(\(\d{3}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}$"  # TODO: This only matches US numbers.
        )
        if not self.phone_number or not re.match(phone_number_pattern, self.phone_number):
            errors.append(ValidationError(field="phone_number"))

        if not self.first_name:
            errors.append(ValidationError(field="first_name"))

        if not self.last_name:
            errors.append(ValidationError(field="last_name"))

        return errors
