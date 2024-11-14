import strawberry
from sqlalchemy import select

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.reserver_details import (
    ReserverDetails,
)
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.stdlib.util import unwrap


async def list_reserver_details_query(*, info: strawberry.Info[GraphQLContext]) -> list[ReserverDetails]:
    query = select(ReserverDetailsOrm).where(
        ReserverDetailsOrm.account_id == unwrap(info.context.get("authenticated_account_id"))
    )

    async with database.async_session.begin() as db_session:
        results = await db_session.scalars(query)
        response = [ReserverDetails.from_orm(orm) for orm in results]

    return response
