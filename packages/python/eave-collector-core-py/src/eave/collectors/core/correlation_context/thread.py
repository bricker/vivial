import json
import threading
import typing
import urllib.parse

from .base import CONTEXT_NAME, COOKIE_PREFIX, BaseCorrelationContext

# TODO: customer child threads wont share this storage
_local_thread_storage = threading.local()


class ThreadedCorrelationContext(BaseCorrelationContext):
    def _init_storage(self) -> None:
        if not getattr(_local_thread_storage, "eave", None):
            _local_thread_storage.eave = {CONTEXT_NAME: {}}

    def get(self, key: str) -> typing.Any:
        self._init_storage()
        return _local_thread_storage.eave.get(key, None) or _local_thread_storage.eave.get(CONTEXT_NAME, {}).get(
            key, None
        )

    def set(self, key: str, value: typing.Any) -> None:
        self._init_storage()
        _local_thread_storage.eave[CONTEXT_NAME][key] = value

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[str, typing.Any]:
        self._init_storage()
        return _local_thread_storage.eave

    def to_cookie(self) -> str:
        self._init_storage()
        # URL encode the cookie values
        return "; ".join(
            [f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in _local_thread_storage.eave.items()]
        )

    def from_cookies(self, cookies: dict[str, str]) -> None:
        self._init_storage()
        for cookie_name, value in [(k, v) for k, v in cookies.items() if k.startswith(COOKIE_PREFIX)]:
            # URL decode cookie values
            decoded_value = urllib.parse.unquote(value)
            if cookie_name == CONTEXT_NAME:
                # parse context cookie json data
                try:
                    _local_thread_storage.eave[cookie_name].update(json.loads(decoded_value))
                finally:
                    # _init_storage already insures eave[CONTEXT_NAME] is at least empty dict, so noop
                    pass
            else:
                _local_thread_storage.eave[cookie_name] = decoded_value
