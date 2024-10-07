from typing import Optional
from uuid import UUID

import strawberry

@strawberry.type
class AuthenticatedUser:
    id: UUID = strawberry.field()
    email: Optional[str] = strawberry.field()

    @classmethod
    def from_orm(cls, orm: AccountOrm) -> "AuthenticatedAccount":
        return AuthenticatedAccount(
            id=orm.id,
            auth_provider=AuthProvider(value=orm.auth_provider),
            visitor_id=orm.visitor_id,
            team_id=orm.team_id,
            opaque_utm_params=orm.opaque_utm_params,
            email=orm.email,
        )