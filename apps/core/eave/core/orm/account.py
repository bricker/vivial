import hashlib
import hmac
import os
import re
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Self, override
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, Select, func, select
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.orm.account_bookings_join_table import ACCOUNT_BOOKINGS_JOIN_TABLE
from eave.core.orm.util.mixins import GetOneByIdMixin
from eave.core.shared.errors import ValidationError
from eave.stdlib.typing import NOT_SET
from eave.stdlib.util import b64encode

from .base import Base
from .util.constants import PG_UUID_EXPR

if TYPE_CHECKING:
    from eave.core.orm.booking import BookingOrm
    from eave.core.orm.outing_preferences import OutingPreferencesOrm
    from eave.core.orm.reserver_details import ReserverDetailsOrm


class InvalidPasswordError(Exception):
    pass


class WeakPasswordError(Exception):
    pass


def validate_password_strength_or_exception(*, plaintext_password: str) -> Literal[True]:
    if (
        plaintext_password
        and len(plaintext_password) >= 8
        and len(plaintext_password) < 256  # This is just to keep memory usage reasonable while hashing
        and re.search("[0-9]", plaintext_password)
        and re.search("[a-zA-Z]", plaintext_password)
        and re.search("[^a-zA-Z0-9]", plaintext_password)
    ):
        return True
    else:
        raise WeakPasswordError()


def _derive_password_key(*, plaintext_password: str, salt: bytes) -> str:
    if not plaintext_password:
        raise ValueError("invalid password")

    # I'm just using the recommended parameter values from the RFC here: https://datatracker.ietf.org/doc/html/rfc7914.html#section-2
    hashed = hashlib.scrypt(
        password=plaintext_password.encode(),
        salt=salt,
        n=pow(2, 14),  # This is based on some benchmarking
        r=8,
        p=1,
    )

    return b64encode(hashed)


class AccountOrm(Base, GetOneByIdMixin):
    __tablename__ = "accounts"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_key_salt: Mapped[str] = mapped_column()
    """hex encoded byte string"""
    password_key: Mapped[str] = mapped_column()
    last_login: Mapped[datetime | None] = mapped_column(
        type_=TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=True
    )
    stripe_customer_id: Mapped[str | None] = mapped_column()

    bookings: Mapped[list["BookingOrm"]] = relationship(
        secondary=ACCOUNT_BOOKINGS_JOIN_TABLE, lazy="selectin", back_populates="accounts"
    )

    outing_preferences: Mapped["OutingPreferencesOrm | None"] = relationship(back_populates="account", lazy="selectin")
    reserver_details: Mapped[list["ReserverDetailsOrm"]] = relationship(back_populates="account", lazy="selectin")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        email: str,
        plaintext_password: str,
    ) -> None:
        self.email = email
        self.set_password(plaintext_password=plaintext_password)

        if session:
            session.add(self)

    @override
    @classmethod
    def select(cls, *, email: str = NOT_SET) -> Select[tuple[Self]]:
        query = select(cls)

        if email is not NOT_SET:
            query = query.where(cls.email == email)

        return query

    def get_booking(self, *, booking_id: UUID) -> "BookingOrm | None":
        # This is more efficient than querying the database directly, because we're already eager-loading account.bookings
        return next((b for b in self.bookings if b.id == booking_id), None)

    @override
    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        # This is deliberately simple, for basic data integrity - the client has a much more robust email validator.
        email_pattern = r"^.+?@.+?\..+$"
        if re.match(email_pattern, self.email) is None:
            errors.append(ValidationError(subject="account", field="email"))

        return errors

    def verify_password_or_exception(self, *, plaintext_password: str) -> Literal[True]:
        expected_password_key = _derive_password_key(
            plaintext_password=plaintext_password, salt=bytes.fromhex(self.password_key_salt)
        )

        # This isn't using hmac but this comparison function is resistant to timing attacks.
        matched = hmac.compare_digest(expected_password_key, self.password_key)
        if matched:
            return True
        else:
            raise InvalidPasswordError()

    def set_password(self, *, plaintext_password: str) -> None:
        if validate_password_strength_or_exception(plaintext_password=plaintext_password):
            salt = os.urandom(16)
            password_key = _derive_password_key(plaintext_password=plaintext_password, salt=salt)
            self.password_key_salt = salt.hex()
            self.password_key = password_key

    def get_default_reserver_details(self) -> "ReserverDetailsOrm | None":
        if len(self.reserver_details) > 0:
            return self.reserver_details[0]
        else:
            return None
