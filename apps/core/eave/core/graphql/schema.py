import strawberry
from graphql import ASTValidationRule
from graphql.error import GraphQLError
from graphql.validation import NoSchemaIntrospectionCustomRule
from strawberry.extensions import (
    AddValidationRules,
    MaskErrors,
    MaxAliasesLimiter,
    MaxTokensLimiter,
    QueryDepthLimiter,
)
from strawberry.schema.config import StrawberryConfig

from eave.core.graphql.extensions.client_geolocation_extension import ClientGeolocationExtension
from eave.core.graphql.extensions.operation_info_extension import OperationInfoExtension
from eave.core.graphql.extensions.visitor_id_extension import VisitorIdExtension
from eave.stdlib.config import SHARED_CONFIG

from .mutation import Mutation
from .query import Query

_validation_rules: list[type[ASTValidationRule]] = []

if not SHARED_CONFIG.is_local:
    _validation_rules.append(NoSchemaIntrospectionCustomRule)


def _should_mask_error(error: GraphQLError) -> bool:
    return True


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(auto_camel_case=True, disable_field_suggestions=(not SHARED_CONFIG.is_local)),
    extensions=[
        AddValidationRules(_validation_rules),
        QueryDepthLimiter(max_depth=10),
        MaxAliasesLimiter(max_alias_count=15),
        MaxTokensLimiter(max_token_count=1000),
        OperationInfoExtension(),
        VisitorIdExtension(),
        ClientGeolocationExtension(),
        MaskErrors(
            error_message="Internal Server Error",
            should_mask_error=_should_mask_error,
        ),
    ],
)
