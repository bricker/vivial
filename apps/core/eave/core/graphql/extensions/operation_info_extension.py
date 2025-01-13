import time
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import cast, override
from uuid import uuid4

from strawberry.extensions import SchemaExtension

from eave.core.graphql.context import GraphQLContext, log_ctx
from eave.stdlib.logging import LOGGER


class OperationInfoExtension(SchemaExtension):
    @override
    def on_operation(self) -> Iterator[None]:
        """
        Outer-most hook. Wraps parsing, validation, and execution.
        Because the operation hasn't been parsed, information about the operation (eg name) isn't available yet.
        """

        perf_start = time.perf_counter()
        ctx = cast(GraphQLContext, self.execution_context.context)

        try:
            # This try/except block is runtime safety because `context` is typed as "Any" and we're force-casting.
            ctx["operation_start_datetime_iso"] = datetime.now(UTC).isoformat()
            ctx.setdefault("correlation_id", uuid4().hex)
            ctx.setdefault("extra", {})

        except Exception as e:
            LOGGER.exception(e, log_ctx(ctx))

        yield

        try:
            ctx["operation_duration"] = time.perf_counter() - perf_start
        except Exception as e:
            LOGGER.exception(e, log_ctx(ctx))

        # Operation name is only available after document parsing has occurred
        # So this property is empty before `yield` here, which is why we have to log the "Executing" message in the `on_execute` hook.
        # But we put the "Complete" message here so that the log_ctx has the status code.
        operation_name = ctx.get("operation_name") or "UNKNOWN"
        LOGGER.info(f"GraphQL Operation Complete: {operation_name}", log_ctx(ctx))

    @override
    def on_execute(self) -> Iterator[None]:
        """
        Inner-most hook.
        At this point, the operation info (eg name) is available.
        """

        ctx = cast(GraphQLContext, self.execution_context.context)
        operation_name = self.execution_context.operation_name

        try:
            # This try/except block is runtime safety because `context` is typed as "Any" and we're force-casting.
            ctx["operation_name"] = operation_name
            ctx["operation_type"] = self.execution_context.operation_type.name

        except Exception as e:
            LOGGER.exception(e, log_ctx(ctx))

        LOGGER.info(f"GraphQL Operation Executing: {operation_name}", log_ctx(ctx))

        yield
