import strawberry


@strawberry.input
class CategoryInput:
    id: str
    subcategory_id: str | None = strawberry.UNSET
