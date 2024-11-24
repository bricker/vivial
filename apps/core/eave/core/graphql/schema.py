from typing import TYPE_CHECKING, Any
from strawberry import Schema, Info
from strawberry.schema.config import StrawberryConfig
from strawberry.extensions import MaskErrors, QueryDepthLimiter, MaxAliasesLimiter, MaxTokensLimiter, AddValidationRules, SchemaExtension
from graphql.validation import NoSchemaIntrospectionCustomRule
from graphql.error import GraphQLError
from graphql import ASTValidationRule

from eave.stdlib.config import SHARED_CONFIG

from eave.core.graphql.context import GraphQLContext

from .query import Query
from .mutation import Mutation

_validation_rules: list[type[ASTValidationRule]] = []

if not SHARED_CONFIG.is_local:
    _validation_rules.append(NoSchemaIntrospectionCustomRule)


def _should_mask_error(error: GraphQLError) -> bool:
    return True


schema = Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(
        auto_camel_case=True,
    ),
    extensions=[
        # Security extensions
        AddValidationRules(_validation_rules),
        MaskErrors(
            error_message="Internal Server Error",
            should_mask_error=_should_mask_error,
        ),
        QueryDepthLimiter(max_depth=10),
        MaxAliasesLimiter(max_alias_count=15),
        MaxTokensLimiter(max_token_count=1000),
    ],
)