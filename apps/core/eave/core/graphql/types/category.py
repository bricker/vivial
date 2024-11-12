from uuid import UUID

import strawberry


@strawberry.type
class Category:
    id: UUID
    label: str
    subcategory_id: UUID | None = None
    subcategory_label: str | None = None
    is_default: bool


@strawberry.input
class CategoryInput:
    id: str
    subcategory_id: str | None = strawberry.UNSET
