import strawberry

from .preferences import UpdatePreferencesInput


@strawberry.input
class UpdateAccountInput:
    first_name: str | None = strawberry.UNSET
    last_name: str | None = strawberry.UNSET
    email: str | None = strawberry.UNSET
    plaintext_password: str | None = strawberry.UNSET
    phone_number: str | None = strawberry.UNSET
    preferences: UpdatePreferencesInput | None = strawberry.UNSET
