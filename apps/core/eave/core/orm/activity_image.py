from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ActivityImageOrm(Base):
    __tablename__ = "activity_images"
    __table_args__ = (
        PrimaryKeyConstraint("activity_id", "image_id"),
        ForeignKeyConstraint(columns=["activity_id"], refcolumns=["activities.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(columns=["image_id"], refcolumns=["images.id"], ondelete="CASCADE"),
    )

    activity_id: Mapped[UUID] = mapped_column()
    image_id: Mapped[UUID] = mapped_column()
