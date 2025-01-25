from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.orm.reserver_details import ReserverDetailsOrm


async def admin_reserver_details_query(
    *,
    info: strawberry.Info[GraphQLContext],
    reserver_details_id: UUID,
) -> ReserverDetails | None:
    async with database.async_session.begin() as session:
        lookup = ReserverDetailsOrm.select().where(ReserverDetailsOrm.id == reserver_details_id)
        details = await session.scalar(lookup)

    if details:
        return ReserverDetails.from_orm(details)
    return None
