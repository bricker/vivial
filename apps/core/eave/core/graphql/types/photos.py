from typing import Self
from uuid import UUID
import strawberry

from eave.core.orm.image import ImageOrm


@strawberry.type
class Photo:
    id: str
    src: str
    alt: str | None

    @classmethod
    def from_orm(cls, orm: ImageOrm) -> "Photo":
        return Photo(
            id=str(orm.id),
            src=orm.src,
            alt=orm.alt,
        )
