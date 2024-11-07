import strawberry

from .category import CategoryInput


@strawberry.input
class PreferencesInput:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_categories: list[CategoryInput]
    activity_categories: list[CategoryInput]


@strawberry.input
class UpdatePreferencesInput:
    open_to_bars: bool | None = strawberry.UNSET
    requires_wheelchair_accessibility: bool | None = strawberry.UNSET
    restaurant_categories: list[CategoryInput] | None = strawberry.UNSET
    activity_categories: list[CategoryInput] | None = strawberry.UNSET
