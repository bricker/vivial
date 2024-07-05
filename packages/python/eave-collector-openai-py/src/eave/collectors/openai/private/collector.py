from typing import Any, Callable
import time
from eave.collectors.core.datastructures import OpenAIChatCompletionEventPayload
import openai.resources.chat
from openai.types.chat import ChatCompletion
from openai import OpenAI, AsyncOpenAI
from eave.collectors.core.base_ai_collector import BaseAICollector
from eave.collectors.core.write_queue import WriteQueue
from eave.collectors.core.correlation_context import CORR_CTX


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

# TODO: look at collectors.core.wrap_util
# def _mark_instrumentation(module: Any) -> None:
#     setattr(module, _INSTRUMENTATION_MARKER_PROPERTY, True)


# def _is_instrumented(module: Any) -> bool:
#     return getattr(module, _INSTRUMENTATION_MARKER_PROPERTY, False)


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

    def _wrap_chat_completion_sync(self, wrapped: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            resp: ChatCompletion = wrapped(*args, **kwargs)
            self.write_queue.put(
                OpenAIChatCompletionEventPayload(
                    timestamp=time.time(),
                    completion_id=resp.id,
                    completion_created_timestamp=resp.created,
                    completion_user_id=kwargs.get("user"),
                    service_tier=resp.service_tier,
                    model=resp.model,
                    num_completions=len(resp.choices),
                    max_tokens=kwargs.get("max_tokens"),
                    prompt_tokens=resp.usage.prompt_tokens if resp.usage else None,
                    completion_tokens=resp.usage.completion_tokens if resp.usage else None,
                    total_tokens=resp.usage.total_tokens if resp.usage else None,
                    corr_ctx=CORR_CTX.to_dict(),
                )
            )
            return resp

        return wrapper

    async def _wrap_function_async(): ...

    def instrument(self, client: OpenAI | AsyncOpenAI | None = None) -> None:
        self.run()
        if client:
            # instrument specific object
            if og_create := getattr(client.chat.completions, "create"):
                setattr(client.chat.completions, "create", self._wrap_chat_completion_sync(og_create))
        else:
            # instrument class itself
            # openai._base_client.BaseClient._process_response_data
            # TODO: attr checks
            if og_create := getattr(openai.resources.chat.Completions, "create"):
                setattr(openai.resources.chat.Completions, "create", self._wrap_chat_completion_sync(og_create))

    def uninstrument(self) -> None:
        pass
