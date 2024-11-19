import enum
from typing import Annotated

import strawberry
import stripe

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.payment_intent import PaymentIntent
from eave.core.shared.errors import ValidationError
from eave.stdlib.util import unwrap


@strawberry.input
class CreatePaymentIntentInput:
    placeholder: str


@strawberry.type
class CreatePaymentIntentSuccess:
    payment_intent: PaymentIntent


@strawberry.enum
class CreatePaymentIntentFailureReason(enum.Enum):
    PAYMENT_INTENT_FAILED = enum.auto()
    UNKNOWN = enum.auto()


@strawberry.type
class CreatePaymentIntentFailure:
    failure_reason: CreatePaymentIntentFailureReason
    validation_errors: list[ValidationError] | None = None


CreatePaymentIntentResult = Annotated[
    CreatePaymentIntentSuccess | CreatePaymentIntentFailure, strawberry.union("CreatePaymentIntentResult")
]


async def create_payment_intent_mutation(
    *, info: strawberry.Info[GraphQLContext], input: CreatePaymentIntentInput
) -> CreatePaymentIntentResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))
    print(account_id)
    # async with database.async_session.begin() as db_session:
    #     booking = await BookingOrm.get_one(db_session, id=input.booking_id)

    stripe_payment_intent = await stripe.PaymentIntent.create_async(
        currency="usd",
        amount=100,  # TODO: Use real amount
    )

    client_secret = stripe_payment_intent.client_secret
    if not client_secret:
        return CreatePaymentIntentFailure(failure_reason=CreatePaymentIntentFailureReason.PAYMENT_INTENT_FAILED)

    # Warning: `client_secret` is a sensitive value and shouldn't be logged.
    payment_intent = PaymentIntent(client_secret=client_secret)
    return CreatePaymentIntentSuccess(payment_intent=payment_intent)
