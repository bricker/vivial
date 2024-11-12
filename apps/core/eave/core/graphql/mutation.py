import strawberry

from eave.core.graphql.resolvers.create_account import create_account_mutation
from eave.core.graphql.resolvers.create_booking import create_booking_mutation
from eave.core.graphql.resolvers.login import login_mutation
from eave.core.graphql.resolvers.logout import logout_mutation
from eave.core.graphql.resolvers.plan_outing import plan_outing_mutation
from eave.core.graphql.resolvers.refresh_tokens import refresh_tokens_mutation
from eave.core.graphql.resolvers.replan_outing import replan_outing_mutation
from eave.core.graphql.resolvers.submit_reserver_details import submit_reserver_details_mutation
from eave.core.graphql.resolvers.update_account import update_account_mutation


@strawberry.type
class Mutation:
    create_account = strawberry.mutation(resolver=create_account_mutation)
    login = strawberry.mutation(resolver=login_mutation)
    refresh_tokens = strawberry.mutation(resolver=refresh_tokens_mutation)
    logout = strawberry.mutation(resolver=logout_mutation)
    plan_outing = strawberry.mutation(resolver=plan_outing_mutation)
    replan_outing = strawberry.mutation(resolver=replan_outing_mutation)
    submit_reserver_details = strawberry.mutation(resolver=submit_reserver_details_mutation)
    create_booking = strawberry.mutation(resolver=create_booking_mutation)
    update_account = strawberry.mutation(resolver=update_account_mutation)
