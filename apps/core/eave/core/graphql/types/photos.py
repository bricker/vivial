import strawberry

from eave.core.orm.image import ImageOrm


@strawberry.type
class Photo:
    id: str
    src: str
    alt: str | None
    attributions: list[str]

    @classmethod
    def from_orm(cls, orm: ImageOrm) -> "Photo":
        return Photo(
            id=str(orm.id),
            src=orm.src,
            alt=orm.alt,
            attributions=[],  # TODO: Add attributions to ImageOrm
        )


@strawberry.type
class Photos:
    cover_photo: Photo | None
    supplemental_photos: list[Photo]
