from typing import Any, Awaitable, Coroutine
from uuid import UUID, uuid4
from eave.core.graphql.types.mutation_result import MutationResult
import eave.core.internal.database as eave_db
import strawberry

@strawberry.type
class Mutation:
    login = strawberry.mutation(resolver=x)
