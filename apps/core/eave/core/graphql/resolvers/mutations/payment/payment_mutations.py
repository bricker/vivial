import strawberry

from eave.core.graphql.resolvers.mutations.payment.create_payment_intent import create_payment_intent_mutation


@strawberry.type
class PaymentMutations:
    create_payment_intent = strawberry.mutation(resolver=create_payment_intent_mutation)
