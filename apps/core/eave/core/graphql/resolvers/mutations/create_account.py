import enum
from textwrap import dedent
from typing import Annotated

import strawberry

import eave.core.database
from eave.core.auth_cookies import set_new_auth_cookies
from eave.core.graphql.context import GraphQLContext, analytics_ctx, log_ctx
from eave.core.graphql.types.account import Account
from eave.core.lib.analytics_client import ANALYTICS
from eave.core.mail import send_welcome_email
from eave.core.orm.account import AccountOrm, WeakPasswordError
from eave.core.orm.base import InvalidRecordError
from eave.core.shared.errors import ValidationError
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.slack import get_authenticated_eave_system_slack_client


@strawberry.input
class CreateAccountInput:
    email: str
    plaintext_password: str


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
    visitor_id = info.context.get("visitor_id")

    try:
        async with eave.core.database.async_session.begin() as db_session:
            existing_account_orm = await db_session.scalar(AccountOrm.select(email=input.email).limit(1))
            if existing_account_orm:
                return CreateAccountFailure(failure_reason=CreateAccountFailureReason.ACCOUNT_EXISTS)

            new_account_orm = AccountOrm(
                db_session,
                email=input.email,
                plaintext_password=input.plaintext_password,
            )

    except InvalidRecordError as e:
        return CreateAccountFailure(
            failure_reason=CreateAccountFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
        )
    except WeakPasswordError:
        return CreateAccountFailure(failure_reason=CreateAccountFailureReason.WEAK_PASSWORD)

    ANALYTICS.identify(
        account_id=new_account_orm.id,
        visitor_id=visitor_id,
        extra_properties={
            "email": new_account_orm.email,
        },
    )

    ANALYTICS.track(
        event_name="signup",
        account_id=new_account_orm.id,
        visitor_id=visitor_id,
        ctx=analytics_ctx(info.context),
    )

    set_new_auth_cookies(response=info.context["response"], account_id=new_account_orm.id)

    # TODO: Send in offline queue
    send_welcome_email(to_emails=[new_account_orm.email])
    await _notify_slack(account=new_account_orm)

    account = Account.from_orm(new_account_orm)
    return CreateAccountSuccess(account=account)


async def _notify_slack(
    *,
    account: AccountOrm,
) -> None:
    try:
        channel_id = SHARED_CONFIG.eave_slack_alerts_signups_channel_id
        slack_client = get_authenticated_eave_system_slack_client()

        if slack_client and channel_id:
            slack_response = await slack_client.chat_postMessage(
                channel=channel_id,
                text=f"New account! {account.email}",
            )

            await slack_client.chat_postMessage(
                channel=channel_id,
                thread_ts=slack_response.get("ts"),
                link_names=True,
                text=dedent(f"""
                    - *Account ID*: `{account.id}`
                    - *Email*: `{account.email}`
                    """),
            )
    except Exception as e:
        LOGGER.exception(e)
