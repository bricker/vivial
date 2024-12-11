from datetime import datetime
from typing import Any, Self, cast

from sqlalchemy import MetaData, Select, event, func, select
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, UOWTransaction, mapped_column
from sqlalchemy.util import IdentitySet

from eave.core.shared.errors import ValidationError
from eave.core.database import async_session
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

    async def save(self, session: AsyncSession) -> Self:
        validation_errors = self.validate()
        if len(validation_errors) > 0:
            raise InvalidRecordError(validation_errors)

        session.add(self)
        await session.flush()
        return self

    @classmethod
    def select(cls) -> Select[tuple[Self]]:
        return select(cls)

    def validate(self) -> list[ValidationError]:
        return []

@event.listens_for(Session, "before_flush")
def validate_orm(session: Session, flush_context: UOWTransaction, instances: Any) -> None:
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
