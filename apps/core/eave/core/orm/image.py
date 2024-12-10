from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.util.mixins import GetOneByIdMixin

from .base import Base
from .util.constants import PG_UUID_EXPR


class ImageOrm(Base, GetOneByIdMixin):
    __tablename__ = "images"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    src: Mapped[str] = mapped_column()
    alt: Mapped[str] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        src: str,
        alt: str,
    ) -> "ImageOrm":
        return ImageOrm(
            src=src,
            alt=alt,
        )
