import enum
from typing import Annotated
from uuid import UUID

import strawberry
import stripe

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.mutations.helpers.create_outing import get_outing_total_cost_cents
from eave.core.graphql.types.payment_intent import PaymentIntent
from eave.core.orm.account import AccountOrm
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
        account = await AccountOrm.get_one(db_session, account_id)
        outing_orm = await OutingOrm.get_one(db_session, input.outing_id)

    if account.stripe_customer_id is None:
        stripe_customer = await stripe.Customer.create_async(
            email=account.email,
            source="vivial-core-api",
            metadata={
                "vivial_account_id": str(account.id),
            },
        )

        async with database.async_session.begin() as db_session:
            # We do this in a different session than the one fetching outing_orm because fetching outing_orm loads the
            # associated account, which may be the same as the authed account, in which case the session already has the
            # account attached and an error is thrown. This should not be an issue when account_id is removed from Outing.
            db_session.add(account)
            account.stripe_customer_id = stripe_customer.id

    outing_total_cost_cents = await get_outing_total_cost_cents(outing_orm=outing_orm)

    stripe_payment_intent = await stripe.PaymentIntent.create_async(
        currency="usd",
        amount=outing_total_cost_cents,
        capture_method="manual",
        receipt_email=account.email,
        setup_future_usage="on_session",
        customer=account.stripe_customer_id,
        metadata={
            "vivial_outing_id": str(outing_orm.id),
        },
    )

    if not stripe_payment_intent.client_secret:
        return CreatePaymentIntentFailure(failure_reason=CreatePaymentIntentFailureReason.PAYMENT_INTENT_FAILED)

    async with database.async_session.begin() as db_session:
        StripePaymentIntentReferenceOrm(
            db_session,
            account=account,
            stripe_payment_intent_id=stripe_payment_intent.id,
            outing=outing_orm,
        )

    # Warning: `client_secret` is a sensitive value and shouldn't be logged or stored.
    # https://docs.stripe.com/api/payment_intents/object#payment_intent_object-client_secret
    payment_intent = PaymentIntent(id=stripe_payment_intent.id, client_secret=stripe_payment_intent.client_secret)
    return CreatePaymentIntentSuccess(payment_intent=payment_intent)
