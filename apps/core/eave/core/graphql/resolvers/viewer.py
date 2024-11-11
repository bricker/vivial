from eave.stdlib.util import unwrap
import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.orm.account import AccountOrm


async def viewer_query(*, info: strawberry.Info[GraphQLContext]) -> Account:
    account_id = unwrap(info.context.authenticated_account_id)

    async with database.async_session.begin() as db_session:
        account_orm = await AccountOrm.one_or_exception(
            session=db_session,
            params=AccountOrm.QueryParams(id=account_id)
        )

    return Account.from_orm(account_orm)
