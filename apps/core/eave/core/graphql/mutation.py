from typing import Any, Awaitable, Coroutine
from uuid import UUID, uuid4
import strawberry as sb
from eave.core.graphql.types.mutation_result import MutationResult
import eave.core.internal.database as eave_db

@sb.type
class Mutation:
    login: sb.mutation(resolver=x)
