import hashlib
import hmac
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Self, overload
from uuid import UUID

from eave.stdlib.typing import NOT_SET, Failure, NotSet, Result, Success
from sqlalchemy import PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, validates

from eave.stdlib.exceptions import ValidationError
from eave.stdlib.util import b64encode

from .base import Base
from .util import PG_UUID_EXPR


class InvalidPasswordError(Exception):
    pass


def test_password_strength_or_exception(plaintext_password: str) -> Literal[True]:
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
        raise ValidationError("password")


def derive_password_key(plaintext_password: str, salt: bytes) -> str:
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


class AccountOrm(Base):
    __tablename__ = "accounts"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    email: Mapped[str] = mapped_column(unique=True)
    password_key_salt: Mapped[str] = mapped_column()
    """hex encoded byte string"""
    password_key: Mapped[str] = mapped_column()
    last_login: Mapped[datetime | None] = mapped_column(server_default=func.current_timestamp(), nullable=True)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        email: str,
        plaintext_password: str,
    ) -> Self:
        obj = cls(
            email=email,
        )

        obj.set_password(plaintext_password)
        return obj

    @classmethod
    def select(cls, *, email: str | NotSet = NOT_SET) -> Select[tuple[Self]]:
        query = select(cls)

        if email is not NOT_SET:
            query = query.where(cls.email == email)

        return query

    @validates("email")
    def validate_email(self, key: str, value: str) -> str:
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(email_pattern, value) is None:
            raise ValidationError("email")
        return value

    def verify_password_or_exception(self, plaintext_password: str) -> Literal[True]:
        expected_password_key = derive_password_key(
            plaintext_password=plaintext_password, salt=bytes.fromhex(self.password_key_salt)
        )

        # This isn't using hmac but this comparison function is resistant to timing attacks.
        matched = hmac.compare_digest(expected_password_key, self.password_key)
        if matched:
            return True
        else:
            raise InvalidPasswordError()

    def set_password(self, plaintext_password: str) -> None:
        if test_password_strength_or_exception(plaintext_password):
            salt = os.urandom(16)
            password_key = derive_password_key(plaintext_password=plaintext_password, salt=salt)
            self.password_key_salt = salt.hex()
            self.password_key = password_key
