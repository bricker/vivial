import strawberry


@strawberry.type
class Category:
    id: str
    subcategory_id: str | None


@strawberry.input
class CategoryInput:
    id: str
    subcategory_id: str | None = strawberry.UNSET
