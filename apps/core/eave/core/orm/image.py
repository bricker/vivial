from datetime import datetime
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util.constants import PG_UUID_EXPR


class ImageOrm(Base):
    __tablename__ = "images"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    src: Mapped[str] = mapped_column()
    alt: Mapped[str] = mapped_column()
