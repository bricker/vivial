from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, Select
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.activity import ActivityOrm
from eave.core.orm.image import ImageOrm
from eave.core.orm.util.constants import OnDeleteOption
from eave.stdlib.typing import NOT_SET

from .base import Base


class ActivityImageOrm(Base):
    __tablename__ = "activity_images"
    __table_args__ = (
        PrimaryKeyConstraint("activity_id", "image_id"),
    )

    activity_id: Mapped[UUID] = mapped_column(ForeignKey(f"{ActivityOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    image_id: Mapped[UUID] = mapped_column(ForeignKey(f"{ImageOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))

    @classmethod
    def select(cls, *, activity_id: UUID = NOT_SET) -> Select[tuple[Self]]:
        query = super().select()

        if activity_id is not NOT_SET:
            query = query.where(cls.activity_id == activity_id)

        query = query.join(ImageOrm, cls.image_id == ImageOrm.id)
        return query
