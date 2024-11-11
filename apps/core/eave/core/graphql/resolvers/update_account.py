from typing import Annotated
from uuid import uuid4

import strawberry

from eave.core.graphql.context import GraphQLContext

from ..types.account import Account

MOCK_ACCOUNT = Account(
    id=uuid4(),
    email="lana@vivialapp.com",
)


@strawberry.input
class UpdateAccountInput:
    email: str | None = strawberry.UNSET
    plaintext_password: str | None = strawberry.UNSET


@strawberry.type
class UpdateAccountSuccess:
    account: Account


UpdateAccountResult = Annotated[UpdateAccountSuccess, strawberry.union("UpdateAccountResult")]


async def update_account_mutation(
    *, info: strawberry.Info[GraphQLContext], input: UpdateAccountInput
) -> UpdateAccountResult:
    return UpdateAccountSuccess(account=MOCK_ACCOUNT)
