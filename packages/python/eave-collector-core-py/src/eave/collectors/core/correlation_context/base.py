import abc
import json
import typing
import urllib.parse
from cryptography import fernet
import hashlib

from eave.collectors.core.config import get_eave_credentials

# The cookie prefix MUST match the browser collector
EAVE_COLLECTOR_COOKIE_PREFIX = "_eave."
EAVE_ENCRYPTED_ACCOUNT_COOKIE_NAME = f"{EAVE_COLLECTOR_COOKIE_PREFIX}nca"
STORAGE_ATTR = "_eave_corr_ctx"


class CorrCtxStorage:
    received: dict[str, str]
    updated: dict[str, str]

    def __init__(self) -> None:
        self.received = {}
        self.updated = {}

    def get(self, key: str) -> str | None:
        """Get a value from either storage"""

        updated_value = self.updated.get(key)
        if updated_value is not None:
            return updated_value
        return self.received.get(key)

    def set(self, key: str, value: str | None) -> None:
        """Set a value in updated_context storage"""
        if value is not None:
            creds = get_eave_credentials()
            if creds:
                encryption_key = hashlib.sha256(bytes(creds, "utf-8")).digest()
                encryptor = fernet.Fernet(encryption_key)
                key = encryptor.encrypt(bytes(value, "utf-8")).decode()
                value = encryptor.encrypt(bytes(value, "utf-8")).decode()

            self.updated[key] = value


    def merged(self) -> dict[str, str]:
        """merge received and updated values together"""

        return {**self.received, **self.updated}

    def updated_values_cookies(self) -> list[str]:
        """
        Convert updated_context store to URL encoded cookie strings.

        Only the updated_context values are converted to prevent
        overwriting potentially changed browser cookies with stale values.
        """

        # URL encode the cookie value
        # TODO: cookie settings? expiration?
        return [f"{_ensure_prefix(key)}={_cookify(value)}" for key, value in self.updated.items()]

    def load_from_cookies(self, cookies: dict[str, str]) -> None:
        """Populate received_context storage from COOKIE_PREFIX prefixed cookies"""

        for cookie_name, value in [(k, v) for k, v in cookies.items() if k.startswith(EAVE_COLLECTOR_COOKIE_PREFIX)]:
            # URL decode cookie values
            decoded_value = urllib.parse.unquote(value)
            self.received[cookie_name] = decoded_value


class BaseCorrelationContext(abc.ABC):
    """
    Shared context, meant to be isolated between network requests to a server,
    that stores data necessary to correlate atoms/events together.

    Relies on some external or member storage to isolate data properly.
    Should have a concept of `received_context` store, populated by a `from_cookies()`
    invocation, and a `updated_context` store, where all new data is put
    by `set()`.
    """

    @abc.abstractmethod
    def init_storage(self) -> None: ...

    @abc.abstractmethod
    def get_storage(self) -> CorrCtxStorage | None: ...

    def get(self, key: str) -> str | None:
        """Get a value from either storage"""

        storage = self.get_storage()
        if not storage:
            return None
        return storage.get(_ensure_prefix(key))

    def set(self, key: str, value: str) -> None:
        """Set a value in updated_context storage"""

        storage = self.get_storage()
        if not storage:
            return
        storage.set(_ensure_prefix(key), value)

    def to_dict(self) -> dict[str, str]:
        """Convert entirety of storage to dict"""

        storage = self.get_storage()
        if not storage:
            return {}
        return storage.merged()

    def to_json(self) -> str:
        """Convert entirety of storage to JSON string"""

        return json.dumps(self.to_dict())

    def get_updated_values_cookies(self) -> list[str]:
        """
        Convert updated_context store to URL encoded cookie strings.

        Only the updated_context values are converted to prevent
        overwriting potentially changed browser cookies with stale values.
        """

        storage = self.get_storage()
        if not storage:
            return []
        return storage.updated_values_cookies()

    def from_cookies(self, cookies: dict[str, str]) -> None:
        """Populate received_context storage from COOKIE_PREFIX prefixed cookies"""

        storage = self.get_storage()
        if not storage:
            return
        storage.load_from_cookies(cookies)

    def clear(self) -> None:
        self.init_storage()


def _ensure_prefix(key: str) -> str:
    if not key.startswith(EAVE_COLLECTOR_COOKIE_PREFIX):
        return f"{EAVE_COLLECTOR_COOKIE_PREFIX}{key}"
    return key


def _cookify(value: typing.Any) -> str:
    """make value HTTP cookie safe via URL encoding"""

    if isinstance(value, dict):
        value = json.dumps(value)
    return urllib.parse.quote_plus(str(value))
