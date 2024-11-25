from typing import Annotated

import strawberry

from eave.core.graphql.extensions.authentication_extension import AuthenticationExtension, UnauthenticatedViewer
from eave.core.graphql.resolvers.mutations.create_account import create_account_mutation
from eave.core.graphql.resolvers.mutations.login import login_mutation
from eave.core.graphql.resolvers.mutations.plan_outing import plan_outing_mutation
from eave.core.graphql.resolvers.mutations.replan_outing import replan_outing_mutation
from eave.core.graphql.resolvers.mutations.viewer.viewer_mutations import AuthenticatedViewerMutations


@strawberry.type
class Mutation:
    create_account = strawberry.mutation(resolver=create_account_mutation)
    login = strawberry.mutation(resolver=login_mutation)
    plan_outing = strawberry.mutation(
        resolver=plan_outing_mutation, extensions=[AuthenticationExtension(allow_anonymous=True)]
    )
    replan_outing = strawberry.mutation(
        resolver=replan_outing_mutation, extensions=[AuthenticationExtension(allow_anonymous=True)]
    )

    @strawberry.mutation(extensions=[AuthenticationExtension()])
    def viewer(
        self,
    ) -> Annotated[AuthenticatedViewerMutations | UnauthenticatedViewer, strawberry.union("ViewerMutations")]:
        return AuthenticatedViewerMutations()
