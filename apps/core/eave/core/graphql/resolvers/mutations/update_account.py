import enum
from typing import Annotated
from uuid import uuid4

import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.shared.errors import ValidationError
from eave.stdlib.util import unwrap

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


@strawberry.enum
class UpdateAccountFailureReason(enum.Enum):
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class UpdateAccountFailure:
    failure_reason: UpdateAccountFailureReason
    validation_errors: list[ValidationError] | None = None


UpdateAccountResult = Annotated[UpdateAccountSuccess | UpdateAccountFailure, strawberry.union("UpdateAccountResult")]


async def update_account_mutation(
    *, info: strawberry.Info[GraphQLContext], input: UpdateAccountInput
) -> UpdateAccountResult:
    account_id = unwrap(info.context.authenticated_account_id)
    return UpdateAccountSuccess(account=MOCK_ACCOUNT)
