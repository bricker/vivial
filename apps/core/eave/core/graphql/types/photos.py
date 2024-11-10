import strawberry


@strawberry.type
class Photos:
    cover_photo_uri: str
    supplemental_photo_uris: list[str] | None
