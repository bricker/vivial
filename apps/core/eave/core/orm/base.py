from datetime import datetime
from typing import Any, Self

from sqlalchemy import Select, event, func, select
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, UOWTransaction, mapped_column

from eave.core.shared.errors import ValidationError
from eave.stdlib.logging import LOGGER


class InvalidRecordError(Exception):
    validation_errors: list[ValidationError]

    def __init__(self, validation_errors: list[ValidationError]) -> None:
        self.validation_errors = validation_errors
        super().__init__()


class Base(DeclarativeBase):
    # Fields common to all tables
    created: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(
        type_=TIMESTAMP(timezone=True), server_default=None, onupdate=func.current_timestamp()
    )

    @classmethod
    def select(cls) -> Select[tuple[Self]]:
        return select(cls)

    def validate(self) -> list[ValidationError]:
        return []


@event.listens_for(Session, "before_flush")
def validate_session(session: Session, flush_context: UOWTransaction, instances: Any) -> None:
    """
    Validates all the records before a flush occurs.
    This is done only on flush, because if done earlier (like when an object is added to the session),
    it's possible that the object will become invalid before flush. Like in this scenario:

    account = Account(email: "bryan@eave.fyi", plaintext_password: "unsafe0!")
    session.add(account)
    account.email = "invalid email"

    The caveat is that the whole session must be wrapped in try/catch, otherwise the validation errors won't be caught.
    This does have the benefit of validating everything at once, so the client will receive all validation errors.
    """
    validation_errors: list[ValidationError] = []
    try:
        for obj in session.dirty:
            if isinstance(obj, Base):
                validation_errors.extend(obj.validate())

        for obj in session.new:
            if isinstance(obj, Base):
                validation_errors.extend(obj.validate())

    except Exception as e:
        # If there was some unexpected error during validation, then don't prevent the SQL operation
        LOGGER.exception(e)

    if len(validation_errors) > 0:
        raise InvalidRecordError(validation_errors=validation_errors)
