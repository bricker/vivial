from graphql import ASTValidationRule, GraphQLError, NoSchemaIntrospectionCustomRule
from strawberry.extensions import (
    AddValidationRules,
    MaskErrors,
    MaxAliasesLimiter,
    MaxTokensLimiter,
    QueryDepthLimiter,
    SchemaExtension,
)

from eave.core.graphql.extensions.client_geolocation_extension import ClientGeolocationExtension
from eave.core.graphql.extensions.operation_info_extension import OperationInfoExtension
from eave.stdlib.config import SHARED_CONFIG

_validation_rules: list[type[ASTValidationRule]] = []

if not SHARED_CONFIG.is_local:
    _validation_rules.append(NoSchemaIntrospectionCustomRule)


def _should_mask_error(error: GraphQLError) -> bool:
    return True


def security_schema_extensions() -> list[type[SchemaExtension] | SchemaExtension]:
    return [
        AddValidationRules(_validation_rules),
        QueryDepthLimiter(max_depth=10),
        MaxAliasesLimiter(max_alias_count=15),
        MaxTokensLimiter(max_token_count=1000),
    ]


def mask_errors_schema_extension() -> MaskErrors:
    return MaskErrors(
        error_message="Internal Server Error",
        should_mask_error=_should_mask_error,
    )


def informational_schema_extensions() -> list[type[SchemaExtension] | SchemaExtension]:
    return [
        OperationInfoExtension(),
        ClientGeolocationExtension(),
    ]
