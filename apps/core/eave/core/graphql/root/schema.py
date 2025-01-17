import strawberry
from strawberry.schema.config import StrawberryConfig

from eave.core.graphql.extensions.common import (
    informational_schema_extensions,
    mask_errors_schema_extension,
    security_schema_extensions,
)
from eave.core.graphql.extensions.visitor_id_extension import VisitorIdExtension
from eave.stdlib.config import SHARED_CONFIG

from .mutation import Mutation
from .query import Query

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(auto_camel_case=True, disable_field_suggestions=(not SHARED_CONFIG.is_local)),
    extensions=[
        *security_schema_extensions(),
        *informational_schema_extensions(),
        VisitorIdExtension(),
        mask_errors_schema_extension(),
    ],
)
