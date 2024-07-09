from dataclasses import dataclass
from typing import Any
from collections.abc import Callable
from eave.collectors.core.generator_proxy import GeneratorProxy, AsyncGeneratorProxy
import time
from eave.collectors.core.datastructures import OpenAIChatCompletionEventPayload
from eave.collectors.core.logging import EAVE_LOGGER
from eave.collectors.core.wrap_util import is_wrapped, tag_wrapped, untag_wrapped
import openai.resources.chat
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai import AsyncStream, OpenAI, AsyncOpenAI, Stream
from eave.collectors.core.base_ai_collector import BaseAICollector
from eave.collectors.core.write_queue import WriteQueue
from eave.collectors.core.correlation_context import CORR_CTX


class OpenAICollector(BaseAICollector):
    @dataclass(kw_only=True)
    class WrappedFunction:
        module: object
        func_name: str
        original_function: Callable

    def __init__(self, *, write_queue: WriteQueue | None = None) -> None:
        super().__init__(write_queue=write_queue)

        # `openai` module path to a function, mapped to
        # the function to wrap it with
        self._wrappable_functions = {
            # "Embedding.create",
            # "Embedding.acreate",
            "resources.chat.Completions.create": self._wrap_chat_completion_sync,
            "resources.chat.AsyncCompletions.create": self._wrap_chat_completion_async,
        }

        self._wrapped_functions: list[OpenAICollector.WrappedFunction] = []

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
            self._add_usage_stream_options(kwargs)
            result: ChatCompletion | AsyncStream = await wrapped(*args, **kwargs)
            if isinstance(result, AsyncStream):
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

    def _get_module_and_func_name(self, target: str) -> tuple[object, str] | None:
        target_path_segments = target.split(".")
        curr_module = openai
        i = 0
        while i < len(target_path_segments) - 1:
            if hasattr(curr_module, target_path_segments[i]):
                curr_module = getattr(curr_module, target_path_segments[i])
            else:
                # cant wrap a module that doesnt exist
                return None
            i += 1

        return curr_module, target_path_segments[i]

    def _wrap_module_method(self, target: str, wrapper: Callable) -> None:
        if mod_and_func := self._get_module_and_func_name(target=target):
            mod, func_name = mod_and_func
            self._wrap_method(mod, func_name, wrapper)

    def _wrap_method(self, target: Any, func_name: str, wrapper: Callable) -> None:
        """Wrap the function at `target`.`func_name` with `wrapper`. Returns the
        original function that got wrapped, if a wrap was performed."""
        if og_func := getattr(target, func_name, None):
            # don't double wrap a function
            if not is_wrapped(og_func):
                wrapped_func = wrapper(og_func)
                setattr(target, func_name, wrapped_func)
                tag_wrapped(wrapped_func)

                # save wrapped function info for later uninstrumentation
                self._wrapped_functions.append(
                    OpenAICollector.WrappedFunction(
                        module=target,
                        func_name=func_name,
                        original_function=og_func,
                    )
                )
        else:
            EAVE_LOGGER.error(f"Failed to find function '{func_name}' in module {target}")

    def instrument(self, client: OpenAI | AsyncOpenAI | None = None) -> None:
        self.run()

        # instrument specific object
        if isinstance(client, openai.OpenAI):
            # TODO: can we abstract these somehow?
            self._wrap_method(client.chat.completions, "create", self._wrap_chat_completion_sync)
        elif isinstance(client, openai.AsyncOpenAI):
            self._wrap_method(client.chat.completions, "create", self._wrap_chat_completion_async)

        # instrument class modules itself
        for mod_path, wrap_function in self._wrappable_functions.items():
            self._wrap_module_method(target=mod_path, wrapper=wrap_function)

    def uninstrument(self) -> None:
        for wrapped_data in self._wrapped_functions:
            setattr(wrapped_data.module, wrapped_data.func_name, wrapped_data.original_function)


## TO SUPPORT:
## - Completions.create / AsyncCompletions.create
## - Stream._iter_events / AsyncStream._iter_events
## - Embeddings (eventually)
