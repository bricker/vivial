from typing import Any
import openai
from openai import OpenAI, AsyncOpenAI
from eave.collectors.core.base_ai_collector import BaseAICollector
from eave.collectors.core.write_queue import WriteQueue

_INSTRUMENTATION_MARKER_PROPERTY = "_eave_instrumented"


"""
openai._base_client

def instrument_openai_base_client(module):
    if hasattr(module, "BaseClient") and hasattr(module.BaseClient, "_process_response"):
        wrap_function_wrapper(module, "BaseClient._process_response", wrap_base_client_process_response_sync)
    else:
        if hasattr(module, "SyncAPIClient") and hasattr(module.SyncAPIClient, "_process_response"):
            wrap_function_wrapper(module, "SyncAPIClient._process_response", wrap_base_client_process_response_sync)
        if hasattr(module, "AsyncAPIClient") and hasattr(module.AsyncAPIClient, "_process_response"):
            wrap_function_wrapper(module, "AsyncAPIClient._process_response", wrap_base_client_process_response_async)

"""

def _mark_instrumentation(module: Any) -> None:
    setattr(module, _INSTRUMENTATION_MARKER_PROPERTY, True)


def _is_instrumented(module: Any) -> bool:
    return getattr(module, _INSTRUMENTATION_MARKER_PROPERTY, False)


class OpenAICollector(BaseAICollector):
    def __init__(self, *, write_queue: WriteQueue | None = None) -> None:
        super().__init__(write_queue=write_queue)

        # functions we can wrap in the `openai` module
        self._wrappable_modules = [
            # "Embedding.create",
            # "Embedding.acreate",
            # "Completions.create",
            # "AsyncCompletions.create",
            "openai.api_resources.chat_completion.ChatCompletion.create",
            "openai.api_resources.chat_completion.ChatCompletion.acreate",
        ]

    def _wrap_function(self, func: str) -> None:
        ...

    def instrument(self, client: OpenAI | AsyncOpenAI | None = None) -> None:
        self.run()
        if client:
            # instrument specific object
            pass
        else:
            # instrument class itself
            openai._base_client.BaseClient._process_response_data


    def uninstrument(self) -> None:
        pass
