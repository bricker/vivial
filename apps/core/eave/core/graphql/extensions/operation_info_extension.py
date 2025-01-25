import time
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import cast, override
from uuid import uuid4

from strawberry.extensions import SchemaExtension

from eave.core.graphql.context import GraphQLContext, log_ctx
from eave.stdlib.exceptions import suppress_in_production
from eave.stdlib.logging import LOGGER


class OperationInfoExtension(SchemaExtension):
    @override
    def on_operation(self) -> Iterator[None]:
        """
        Outer-most hook. Wraps parsing, validation, and execution.
        Because the operation hasn't been parsed, information about the operation (eg name) isn't available yet.
        """

        perf_start = time.perf_counter()
        gql_ctx = cast(GraphQLContext, self.execution_context.context)

        with suppress_in_production(Exception, ctx=log_ctx(gql_ctx)):
            # This try/except block is runtime safety because `context` is typed as "Any" and we're force-casting.
            gql_ctx["operation_start_datetime_iso"] = datetime.now(UTC).isoformat()
            gql_ctx.setdefault("correlation_id", uuid4().hex)
            gql_ctx.setdefault("extra", {})

        yield

        with suppress_in_production(Exception, ctx=log_ctx(gql_ctx)):
            gql_ctx["operation_duration"] = time.perf_counter() - perf_start

        # Operation name is only available after document parsing has occurred
        # So this property is empty before `yield` here, which is why we have to log the "Executing" message in the `on_execute` hook.
        # But we put the "Complete" message here so that the log_ctx has the status code.
        operation_name = gql_ctx.get("operation_name") or "UNKNOWN"
        LOGGER.info(f"GraphQL Operation Complete: {operation_name}", log_ctx(gql_ctx))

    @override
    def on_execute(self) -> Iterator[None]:
        """
        Inner-most hook.
        At this point, the operation info (eg name) is available.
        """

        gql_ctx = cast(GraphQLContext, self.execution_context.context)
        operation_name = self.execution_context.operation_name

        with suppress_in_production(Exception, ctx=log_ctx(gql_ctx)):
            # This try/except block is runtime safety because `context` is typed as "Any" and we're force-casting.
            gql_ctx["operation_name"] = operation_name
            gql_ctx["operation_type"] = self.execution_context.operation_type.name

        LOGGER.info(f"GraphQL Operation Executing: {operation_name}", log_ctx(gql_ctx))

        yield
