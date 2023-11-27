from typing import Optional
from uuid import UUID
import strawberry.federation as sb

@sb.type
class AuthenticatedAccount:
    id: UUID = sb.field()
    auth_provider: AuthProvider = sb.field()
    visitor_id: Optional[UUID] = sb.field()
    team_id: UUID = sb.field()
    opaque_utm_params: Optional[Mapping[str, Any]] = sb.field()
    email: Optional[str] = sb.field()

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
