import contextvars
import json
import typing
import urllib.parse

from .base import CONTEXT_NAME, COOKIE_PREFIX, BaseCorrelationContext

_local_async_storage = contextvars.ContextVar("eave_corr_ctx")


class AsyncioCorrelationContext(BaseCorrelationContext):
    def _get_storage(self) -> dict[str, typing.Any]:
        eave_ctx = contextvars.copy_context().get(_local_async_storage, None)
        if not eave_ctx:
            _local_async_storage.set({CONTEXT_NAME: {}})
            # refetch ctx vars now that we've set a value
            eave_ctx = contextvars.copy_context().get(_local_async_storage)
        return typing.cast(dict[str, typing.Any], eave_ctx)

    def get(self, key: str) -> typing.Any:
        storage = self._get_storage()
        return storage.get(key, None) or storage.get(CONTEXT_NAME, {}).get(key, None)

    def set(self, key: str, value: typing.Any) -> None:
        storage = self._get_storage()
        storage[CONTEXT_NAME][key] = value

    def to_dict(self) -> dict[str, typing.Any]:
        storage = self._get_storage()
        return storage

    def to_cookie(self) -> str:
        storage = self._get_storage()
        # URL encode the cookie values
        encoded_json_ctx_value = urllib.parse.quote_plus(json.dumps(storage[CONTEXT_NAME]))
        return f"{CONTEXT_NAME}={encoded_json_ctx_value}"

    def from_cookies(self, cookies: dict[str, str]) -> None:
        storage = self._get_storage()
        for cookie_name, value in [(k, v) for k, v in cookies.items() if k.startswith(COOKIE_PREFIX)]:
            # URL decode cookie values
            decoded_value = urllib.parse.unquote(value)
            if cookie_name == CONTEXT_NAME:
                # parse context cookie json data
                try:
                    storage[cookie_name].update(json.loads(decoded_value))
                except json.decoder.JSONDecodeError:
                    # _init_storage already insures eave[CONTEXT_NAME] is at least empty dict, so noop
                    pass
            else:
                storage[cookie_name] = decoded_value
