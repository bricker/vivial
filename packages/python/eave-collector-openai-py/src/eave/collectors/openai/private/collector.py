from typing import Any
from collections.abc import Callable
from eave.collectors.core.generator_proxy import GeneratorProxy, AsyncGeneratorProxy
import time
from eave.collectors.core.datastructures import OpenAIChatCompletionEventPayload
from eave.collectors.core.logging import EAVE_LOGGER
import openai.resources.chat
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai import AsyncStream, OpenAI, AsyncOpenAI, Stream
from eave.collectors.core.base_ai_collector import BaseAICollector
from eave.collectors.core.write_queue import WriteQueue
from eave.collectors.core.correlation_context import CORR_CTX

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
            "openai.resources.chat.Completions.create",
            "openai.resources.chat.AsyncCompletions.create",
        ]

    def _proxy_stream(
        self, stream: Stream | AsyncStream, completion_handler: Callable[[Any], None], error_handler: Callable
    ) -> None:
        if isinstance(stream, Stream):
            stream._iterator = GeneratorProxy(  # noqa: SLF001
                gen=stream._iterator,  # noqa: SLF001
                completion_handler=completion_handler,
                error_handler=error_handler,
            )
        elif isinstance(stream, AsyncStream):
            stream._iterator = AsyncGeneratorProxy(  # noqa: SLF001
                gen=stream._iterator,  # noqa: SLF001
                completion_handler=completion_handler,
                error_handler=error_handler,
            )

    def _add_usage_stream_options(self, kwargs: dict[str, Any]) -> None:
        """Add stream usage options if streaming is enabled.
        Modifies kwargs in-place."""
        if kwargs.get("stream", False):
            if options := kwargs.get("stream_options"):
                options["include_usage"] = True
            else:
                kwargs["stream_options"] = {"include_usage": True}

    def _write_chat_completion_event(
        self, chat_response: ChatCompletion | ChatCompletionChunk, chat_args: dict[str, Any]
    ) -> None:
        self.write_queue.put(
            OpenAIChatCompletionEventPayload(
                timestamp=time.time(),
                completion_id=chat_response.id,
                completion_created_timestamp=chat_response.created,
                completion_user_id=chat_args.get("user"),
                service_tier=chat_response.service_tier,
                model=chat_response.model,
                num_completions=len(chat_response.choices),
                max_tokens=chat_args.get("max_tokens"),
                prompt_tokens=chat_response.usage.prompt_tokens if chat_response.usage else None,
                completion_tokens=chat_response.usage.completion_tokens if chat_response.usage else None,
                total_tokens=chat_response.usage.total_tokens if chat_response.usage else None,
                corr_ctx=CORR_CTX.to_dict(),
            )
        )

    def _log_chat_completion_error(self) -> None:
        # TODO: should we bother firing an atom or anything if error
        # is encountered during stream reading?
        ...

    def _wrap_chat_completion_sync(self, wrapped: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            self._add_usage_stream_options(kwargs)
            result: ChatCompletion | Stream = wrapped(*args, **kwargs)
            if isinstance(result, Stream):
                # wrap the stream iter to write atom to queue when stream is consumed
                self._proxy_stream(
                    stream=result,
                    completion_handler=lambda resp: self._write_chat_completion_event(
                        chat_response=resp, chat_args=kwargs
                    ),
                    error_handler=self._log_chat_completion_error,
                )
            else:
                self._write_chat_completion_event(
                    chat_response=result,
                    chat_args=kwargs,
                )
            return result

        return wrapper

    def _wrap_chat_completion_async(self, wrapped: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            # TODO: AsyncStream
            resp: ChatCompletion = await wrapped(*args, **kwargs)
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

    def _wrap_method(self, target: Any, func_name: str, wrapper: Callable) -> None:
        if og_func := getattr(target, func_name, None):
            setattr(target, func_name, wrapper(og_func))
        else:
            EAVE_LOGGER.error(f"Failed to find function '{func_name}' in module {target}")

    def instrument(self, client: OpenAI | AsyncOpenAI | None = None) -> None:
        self.run()
        if isinstance(client, openai.OpenAI):
            # instrument specific sync object
            self._wrap_method(client.chat.completions, "create", self._wrap_chat_completion_sync)
        elif isinstance(client, openai.AsyncOpenAI):
            # instrument specific async object
            self._wrap_method(client.chat.completions, "create", self._wrap_chat_completion_async)
        else:
            # instrument class itself
            # TODO: attr checks?
            self._wrap_method(openai.resources.chat.Completions, "create", self._wrap_chat_completion_sync)
            self._wrap_method(openai.resources.chat.AsyncCompletions, "create", self._wrap_chat_completion_async)

    def uninstrument(self) -> None:
        pass


## TO SUPPORT:
## - Completions.create / AsyncCompletions.create
## - Stream._iter_events / AsyncStream._iter_events
## - Embeddings (eventually)
