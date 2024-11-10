from eave.core.graphql.resolvers.account import MOCK_ACCOUNT
from eave.core.graphql.types.account import Account


async def viewer_query() -> Account:
    return MOCK_ACCOUNT
