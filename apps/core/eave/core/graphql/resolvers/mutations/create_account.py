import enum
from typing import Annotated
from uuid import UUID

import strawberry

import eave.core.database
from eave.core.analytics import ANALYTICS
from eave.core.auth_cookies import set_new_auth_cookies
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.mail import send_welcome_email
from eave.core.orm.account import AccountOrm, WeakPasswordError
from eave.core.orm.base import InvalidRecordError
from eave.core.shared.errors import ValidationError


@strawberry.input
class CreateAccountInput:
    email: str
    plaintext_password: str
    visitor_id: UUID


@strawberry.type
class CreateAccountSuccess:
    account: Account


@strawberry.enum
class CreateAccountFailureReason(enum.Enum):
    ACCOUNT_EXISTS = enum.auto()
    WEAK_PASSWORD = enum.auto()
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class CreateAccountFailure:
    failure_reason: CreateAccountFailureReason
    validation_errors: list[ValidationError] | None = None


CreateAccountResult = Annotated[CreateAccountSuccess | CreateAccountFailure, strawberry.union("CreateAccountResult")]


async def create_account_mutation(
    *, info: strawberry.Info[GraphQLContext], input: CreateAccountInput
) -> CreateAccountResult:
    try:
        async with eave.core.database.async_session.begin() as db_session:
            existing_account_orm = await db_session.scalar(AccountOrm.select(email=input.email).limit(1))
            if existing_account_orm:
                return CreateAccountFailure(failure_reason=CreateAccountFailureReason.ACCOUNT_EXISTS)

            account_orm = AccountOrm(
                email=input.email,
                plaintext_password=input.plaintext_password,
            )
            db_session.add(account_orm)

    except InvalidRecordError as e:
        return CreateAccountFailure(
            failure_reason=CreateAccountFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
        )
    except WeakPasswordError:
        return CreateAccountFailure(failure_reason=CreateAccountFailureReason.WEAK_PASSWORD)

    ANALYTICS.identify(
        account_id=account_orm.id,
        visitor_id=input.visitor_id,
        extra_properties={
            "email": account_orm.email,
        },
    )

    ANALYTICS.track(
        event_name="signup",
        account_id=account_orm.id,
        visitor_id=input.visitor_id,
    )

    set_new_auth_cookies(response=info.context["response"], account_id=account_orm.id)

    send_welcome_email(to_emails=[account_orm.email])

    account = Account.from_orm(account_orm)
    return CreateAccountSuccess(account=account)
