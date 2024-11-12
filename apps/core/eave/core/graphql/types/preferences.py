import strawberry

from eave.core.graphql.types.category import Category, CategoryInput


@strawberry.type
class Preferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_categories: list[Category]
    activity_categories: list[Category]


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
