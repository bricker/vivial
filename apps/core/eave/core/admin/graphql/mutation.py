from typing import Annotated

import strawberry

from eave.core.admin.graphql.resolvers.mutations.update_booking import admin_update_booking_mutation
from eave.core.graphql.extensions.authentication_extension import AuthenticationExtension, UnauthenticatedViewer
from eave.core.graphql.resolvers.mutations.create_account import create_account_mutation
from eave.core.graphql.resolvers.mutations.login import login_mutation
from eave.core.graphql.resolvers.mutations.plan_outing import plan_outing_mutation
from eave.core.graphql.resolvers.mutations.viewer.viewer_mutations import AuthenticatedViewerMutations


@strawberry.type
class Mutation:
    update_booking = strawberry.mutation(resolver=admin_update_booking_mutation)
