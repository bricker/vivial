from collections.abc import Iterator
from typing import TypedDict, cast, override

from asgiref.typing import HTTPScope
from starlette.requests import Request
from strawberry.extensions import SchemaExtension

from eave.core.graphql.context import GraphQLContext, log_ctx
from eave.stdlib.api_util import get_header_value
from eave.stdlib.logging import LOGGER

class ClientGeolocationExtension(SchemaExtension):
    @override
    def on_operation(self) -> Iterator[None]:
        ctx = cast(GraphQLContext, self.execution_context.context)

        try:
            req: Request = ctx["request"]
            cscope = cast(HTTPScope, req.scope)

            # These headers are set by the GCP Load Balancer.
            # They will not be present during local development.
            ctx["client_geo"] = {
                "region": get_header_value(scope=cscope, name="eave-lb-geo-region"),
                "subdivision": get_header_value(scope=cscope, name="eave-lb-geo-subdivision"),
                "city": get_header_value(scope=cscope, name="eave-lb-geo-city"),
                "coordinates": get_header_value(scope=cscope, name="eave-lb-geo-coordinates"),
            }

            client_ip = get_header_value(scope=cscope, name="eave-lb-client-ip")

            if client_ip is None:
                client_attrs = cscope["client"]
                if client_attrs is not None:
                    client_ip, _ = client_attrs

            ctx["client_ip"] = client_ip

        except Exception as e:
            LOGGER.exception(e, log_ctx(ctx))

        yield
