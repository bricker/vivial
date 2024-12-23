import re
from typing import Self, override
from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.orm.account import AccountOrm
from eave.core.shared.errors import ValidationError

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class ReserverDetailsOrm(Base):
    __tablename__ = "reserver_details"
    __table_args__ = (PrimaryKeyConstraint("account_id", "id", name="account_id_id_pk"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()

    account_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    account: Mapped[AccountOrm] = relationship(lazy="selectin", back_populates="reserver_details")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        account: AccountOrm,
        first_name: str,
        last_name: str,
        phone_number: str,
    ) -> None:
        self.account = account
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number

        if session:
            session.add(self)

    @override
    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        phone_number_pattern = (
            r"^(\+?1)?[\s-]?(\(\d{3}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}$"  # TODO: This only matches US numbers.
        )
        if not self.phone_number or not re.match(phone_number_pattern, self.phone_number):
            errors.append(ValidationError(subject="reserver_details", field="phone_number"))

        if not self.first_name:
            errors.append(ValidationError(subject="reserver_details", field="first_name"))

        if not self.last_name:
            errors.append(ValidationError(subject="reserver_details", field="last_name"))

        return errors

    @classmethod
    async def get_one(cls, session: AsyncSession, *, account_id: UUID, uid: UUID) -> Self:
        return await session.get_one(cls, (account_id, uid))
