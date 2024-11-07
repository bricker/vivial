import strawberry

from .preferences import PreferencesInput


@strawberry.type
class UserProfile:
    name: str


@strawberry.input
class UserInput:
    visitor_id: str | None = strawberry.UNSET
    account_id: str | None = strawberry.UNSET
    preferences: PreferencesInput | None = strawberry.UNSET
