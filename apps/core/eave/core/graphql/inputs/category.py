import strawberry


@strawberry.input
class CategoryInput:
    id: str = strawberry.UNSET
    subcategory_id: str | None = strawberry.UNSET
