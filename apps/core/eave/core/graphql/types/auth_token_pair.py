
import strawberry


@strawberry.type
class AuthTokenPair:
    access_token: str
    refresh_token: str
