from collections.abc import Iterator
from typing import override
from uuid import uuid4

from strawberry.extensions import SchemaExtension

from eave.core.graphql.context import log_ctx
from eave.stdlib.logging import LOGGER


class LogContextExtension(SchemaExtension):
    @override
    def on_operation(self) -> Iterator[None]:
        LOGGER.debug("LogContextExtension:on_operation")

        try:
            # Safety because `context` here is typed as "Any"
            self.execution_context.context["request_id"] = str(uuid4())
            self.execution_context.context["extra"] = {}

        except Exception as e:
            LOGGER.exception(e)

        yield

    @override
    def on_execute(self) -> Iterator[None]:
        LOGGER.debug("LogContextExtension:on_execute")
        operation_name = self.execution_context.operation_name

        try:
            # Safety because `context` here is typed as "Any"
            self.execution_context.context["operation_name"] = operation_name
            self.execution_context.context["operation_type"] = self.execution_context.operation_type.name

        except Exception as e:
            LOGGER.exception(e)

        LOGGER.info(f"GraphQL Operation Executing: {operation_name}", log_ctx(self.execution_context.context))

        yield
