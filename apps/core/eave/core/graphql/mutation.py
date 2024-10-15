from typing import Any, Awaitable, Coroutine
from uuid import UUID, uuid4
from eave.core.graphql.resolvers.authentication import login_mutation, logout_mutation, refresh_tokens_mutation, register_mutation
from eave.core.graphql.types.mutation_result import MutationResult
import eave.core.internal.database as eave_db
import strawberry

@strawberry.type
class Mutation:
    register = strawberry.mutation(resolver=register_mutation)
    login = strawberry.mutation(resolver=login_mutation)
    refresh_tokens = strawberry.mutation(resolver=refresh_tokens_mutation)
    logout = strawberry.mutation(resolver=logout_mutation)
