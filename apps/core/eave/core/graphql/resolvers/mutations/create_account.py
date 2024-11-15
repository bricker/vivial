import enum
from typing import Annotated

from eave.stdlib.mail import MAILER
import strawberry

import eave.core.database
from eave.core.analytics import ANALYTICS
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.refresh_tokens import make_auth_token_pair
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.auth_token_pair import AuthTokenPair
from eave.core.orm.account import AccountOrm, WeakPasswordError
from eave.core.orm.base import InvalidRecordError
from eave.core.shared.errors import ValidationError


@strawberry.input
class CreateAccountInput:
    email: str
    plaintext_password: str


@strawberry.type
class CreateAccountSuccess:
    account: Account
    auth_tokens: AuthTokenPair


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
    async with eave.core.database.async_session.begin() as db_session:
        existing_account_orm = await db_session.scalar(AccountOrm.select(email=input.email).limit(1))
        if existing_account_orm:
            return CreateAccountFailure(failure_reason=CreateAccountFailureReason.ACCOUNT_EXISTS)

        try:
            account_orm = await AccountOrm.build(
                email=input.email,
                plaintext_password=input.plaintext_password,
            ).save(db_session)

        except InvalidRecordError as e:
            return CreateAccountFailure(
                failure_reason=CreateAccountFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
            )
        except WeakPasswordError:
            return CreateAccountFailure(failure_reason=CreateAccountFailureReason.WEAK_PASSWORD)

    ANALYTICS.identify(
        account_id=account_orm.id,
        # TODO: visitor_id
        extra_properties={
            "email": account_orm.email,
        },
    )

    ANALYTICS.track(
        event_name="signup",
        account_id=account_orm.id,
    )

    auth_token_pair = make_auth_token_pair(account_id=account_orm.id)

    MAILER.send_welcome_email(to_emails=[account_orm.email])

    account = Account.from_orm(account_orm)
    return CreateAccountSuccess(account=account, auth_tokens=auth_token_pair)
