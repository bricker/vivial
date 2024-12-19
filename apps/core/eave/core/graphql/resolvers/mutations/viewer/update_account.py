import enum
from typing import Annotated

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.orm.account import AccountOrm, WeakPasswordError
from eave.core.orm.base import InvalidRecordError
from eave.core.shared.errors import ValidationError
from eave.stdlib.util import unwrap


@strawberry.input
class UpdateAccountInput:
    email: str | None = strawberry.UNSET
    plaintext_password: str | None = strawberry.UNSET


@strawberry.type
class UpdateAccountSuccess:
    account: Account


@strawberry.enum
class UpdateAccountFailureReason(enum.Enum):
    WEAK_PASSWORD = enum.auto()
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
            account = await AccountOrm.get_one(db_session, account_id)

            if input.email:
                account.email = input.email
            if input.plaintext_password:
                account.set_password(plaintext_password=input.plaintext_password)

        return UpdateAccountSuccess(account=Account.from_orm(account))

    except WeakPasswordError:
        return UpdateAccountFailure(
            failure_reason=UpdateAccountFailureReason.WEAK_PASSWORD,
        )
    except InvalidRecordError as e:
        return UpdateAccountFailure(
            failure_reason=UpdateAccountFailureReason.VALIDATION_ERRORS,
            validation_errors=e.validation_errors,
        )
