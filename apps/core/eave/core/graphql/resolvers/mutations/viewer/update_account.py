import enum
from typing import Annotated
from uuid import uuid4

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.orm.account import AccountOrm, WeakPasswordError
from eave.core.orm.base import InvalidRecordError
from eave.core.shared.errors import ValidationError
from eave.stdlib.util import unwrap

MOCK_ACCOUNT = Account(
    id=uuid4(),
    email="lana@vivialapp.com",
)


@strawberry.input
class UpdateAccountInput:
    email: str | None
    plaintext_password: str | None


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
    account_id = unwrap(info.context.get("authenticated_account_id"))
    try:
        async with database.async_session.begin() as db_session:
            account = await AccountOrm.get_one(
                session=db_session,
                id=account_id,
            )
            if input.email is not None:
                account.email = input.email
            if input.plaintext_password is not None:
                account.set_password(input.plaintext_password)
            await account.save(db_session)

        return UpdateAccountSuccess(account=Account.from_orm(account))

    except WeakPasswordError:
        return UpdateAccountFailure(
            failure_reason=UpdateAccountFailureReason.VALIDATION_ERRORS,
            validation_errors=[ValidationError(field="password")],
        )
    except InvalidRecordError as e:
        return UpdateAccountFailure(
            failure_reason=UpdateAccountFailureReason.VALIDATION_ERRORS,
            validation_errors=e.validation_errors,
        )
