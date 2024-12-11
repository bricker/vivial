import enum
from typing import Annotated
from uuid import UUID

import strawberry
import stripe

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.payment_intent import PaymentIntent
from eave.core.orm.outing import OutingOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.stdlib.util import unwrap


@strawberry.input
class CreatePaymentIntentInput:
    outing_id: UUID


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


CreatePaymentIntentResult = Annotated[
    CreatePaymentIntentSuccess | CreatePaymentIntentFailure, strawberry.union("CreatePaymentIntentResult")
]


async def create_payment_intent_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: CreatePaymentIntentInput,
) -> CreatePaymentIntentResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        outing_orm = await OutingOrm.get_one(db_session, input.outing_id)

    stripe_payment_intent = await stripe.PaymentIntent.create_async(
        currency="usd",
        amount=outing.pricing,
    )

    client_secret = stripe_payment_intent.client_secret
    if not client_secret:
        return CreatePaymentIntentFailure(failure_reason=CreatePaymentIntentFailureReason.PAYMENT_INTENT_FAILED)

    async with database.async_session.begin() as db_session:
        await StripePaymentIntentReferenceOrm(
            account_id=account_id,
            stripe_payment_intent_id=stripe_payment_intent.id,
            outing_id=outing_orm.id,
        ).save(db_session)

    # Warning: `client_secret` is a sensitive value and shouldn't be logged or stored.
    # https://docs.stripe.com/api/payment_intents/object#payment_intent_object-client_secret
    payment_intent = PaymentIntent(client_secret=client_secret)
    return CreatePaymentIntentSuccess(payment_intent=payment_intent)
