from uuid import UUID
import strawberry

from eave.core.graphql.resolvers.outing import get_outing_query
from eave.core.graphql.resolvers.booked_outings import list_booked_outings_query
from eave.core.graphql.resolvers.reserver_details import list_reserver_details_query
from eave.core.graphql.types.outing import Outing
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.orm.account import AccountOrm

from .preferences import Preferences, UpdatePreferencesInput


@strawberry.type
class Account:
    id: UUID
    email: str

    booked_outings: list[Outing] = strawberry.field(resolver=list_booked_outings_query)
    outing: Outing = strawberry.field(resolver=get_outing_query)
    reserver_details: list[ReserverDetails] = strawberry.field(resolver=list_reserver_details_query)

    @classmethod
    def from_orm(cls, orm: AccountOrm) -> "Account":
        return Account(
            id=orm.id,
            email=orm.email,
        )
