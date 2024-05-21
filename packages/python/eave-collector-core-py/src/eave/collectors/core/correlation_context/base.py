import abc
import json
import typing
import urllib.parse

# These values are dependent on the eave browser js client implementation and MUST change
# if those values change in the js client
COOKIE_PREFIX = "_eave_"


class BaseCorrelationContext(abc.ABC):
    """
    Shared context, meant to be isolated between network requests to a server,
    that stores data necessary to correlate atoms/events together.

    Relies on some external or member storage to isolate data properly.
    Should have a concept of `received_context` store, populated by a `from_cookies()`
    invocation, and a `updated_context` store, where all new data is put
    by `set()`.
    """

    def _ensure_prefix(self, key: str) -> str:
        if not key.startswith(COOKIE_PREFIX):
            return f"{COOKIE_PREFIX}{key}"
        return key

    def _cookify(self, value: typing.Any) -> str:
        """make value HTTP cookie safe via URL encoding"""
        if isinstance(value, dict):
            value = json.dumps(value)
        return urllib.parse.quote_plus(str(value))

    @abc.abstractmethod
    def get(self, key: str) -> str:
        """Get a value from either storage"""
        ...

    @abc.abstractmethod
    def set(self, key: str, value: str) -> None:
        """Set a value in updated_context storage"""
        ...

    def to_json(self) -> str:
        """Convert entirity of storage to JSON string"""
        return json.dumps(self.to_dict())

    @abc.abstractmethod
    def to_dict(self) -> dict[str, str]:
        """Convert entirity of storage to dict"""
        ...

    @abc.abstractmethod
    def get_updated_values_cookies(self) -> list[str]:
        """
        Convert updated_context store to URL encoded cookie strings.

        Only the updated_context values are converted to prevent
        overwriting potentially changed browser cookies with stale values.
        """
        ...

    @abc.abstractmethod
    def from_cookies(self, cookies: dict[str, str]) -> None:
        """Populate received_context storage from COOKIE_PREFIX prefixed cookies"""
        ...
