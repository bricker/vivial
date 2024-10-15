from uuid import uuid4
from eave.core.graphql.types.authentication import Account
from eave.core.graphql.types.user_profile import UserProfile


async def viewer_query() -> Account:
    return Account(
        id=uuid4(),
        email="example@vivialapp.com",
        user_profile=UserProfile(name="example"),
    )
