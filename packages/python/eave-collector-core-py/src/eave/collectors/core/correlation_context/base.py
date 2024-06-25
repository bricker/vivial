import abc
import hashlib
import json
import typing
import urllib.parse
from base64 import b64encode
from dataclasses import dataclass

from cryptography import fernet

from eave.collectors.core.config import EaveCredentials
from eave.collectors.core.json import JsonScalar, compact_json
from eave.collectors.core.logging import EAVE_LOGGER

# The cookie prefix MUST match the browser collector
EAVE_COLLECTOR_COOKIE_PREFIX = "_eave."
EAVE_COLLECTOR_ENCRYPTED_COOKIE_PREFIX = f"{EAVE_COLLECTOR_COOKIE_PREFIX}nc."
EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX = f"{EAVE_COLLECTOR_ENCRYPTED_COOKIE_PREFIX}act."
EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME = "account_id"
STORAGE_ATTR = "_eave_corr_ctx"


def corr_ctx_symmetric_encryption_key(credentials: str) -> bytes:
    return b64encode(hashlib.sha256(bytes(credentials, "utf-8")).digest())


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

    def set_encrypted(self, *, prefix: str, key: str, value: JsonScalar | None) -> None:
        """Set a value in updated_context storage"""
        if value is None:
            return None

        creds = EaveCredentials.from_env()
        if not creds:
            return None

        try:
            attr = CorrelationContextAttr(key=key, value=value)
            encryption_key = corr_ctx_symmetric_encryption_key(creds.combined)
            encrypted_attr = attr.to_encrypted(encryption_key=encryption_key)
            if encrypted_attr is None:
                return None

            # The purpose of hashing the key is to obfuscate it from the client (browser), to avoid leaking internal
            # system details. For example, the customer may not want their users knowing about a field called "team_id".
            # It needs to be hashed instead of encrypted because the key must always be the same.
            # Additionally, we prefix the client ID to the key before hashing so that the hash is different across customers.
            # Otherwise, customers would always have the same cookie name for `account_id`, defeating the purpose of the hashing.
            hashedkey = hashlib.sha256(bytes(f"{creds.client_id}{key}", "utf-8")).hexdigest()
            final_key = f"{prefix}{hashedkey}"
            self.updated[final_key] = encrypted_attr
        except Exception as e:
            EAVE_LOGGER.exception(e)
            return None

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
        return [f"{key}={_cookify(value)}" for key, value in self.updated.items()]

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
        return storage.get(key)

    def set_encrypted(self, *, prefix: str, key: str, value: JsonScalar | None) -> None:
        """Set a value in updated_context storage"""

        storage = self.get_storage()
        if not storage:
            return
        storage.set_encrypted(prefix=prefix, key=key, value=value)

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


def _cookify(value: typing.Any) -> str:
    """make value HTTP cookie safe via URL encoding"""

    if isinstance(value, dict):
        value = json.dumps(value)
    return urllib.parse.quote_plus(str(value))


@dataclass(kw_only=True)
class CorrelationContextAttr:
    key: str
    value: JsonScalar | None

    @classmethod
    def from_encrypted(cls, *, decryption_key: bytes, encrypted_value: str) -> typing.Self | None:
        try:
            encryptor = fernet.Fernet(decryption_key)

            # TTL should NOT be considered here, because the encrypted value may come from long-lived cookies.
            # Regardless, this encryption is purely for obfuscation in the browser, not for message integrity, so TTL doesn't really matter.
            decrypted_value = encryptor.decrypt(encrypted_value, ttl=None).decode()
            jvalue = json.loads(decrypted_value)
        except Exception as e:
            EAVE_LOGGER.exception(e)
            return None

        if not isinstance(jvalue, dict):
            return None

        if (key := jvalue.get("key")) is None:
            return None

        return cls(
            key=key,
            value=jvalue.get("value"),
        )

    def to_encrypted(self, *, encryption_key: bytes) -> str | None:
        try:
            encryptor = fernet.Fernet(encryption_key)
            jvalue = compact_json({"key": self.key, "value": self.value})
            encrypted_value = encryptor.encrypt(bytes(jvalue, "utf-8")).decode()
            return encrypted_value
        except Exception as e:
            EAVE_LOGGER.exception(e)
            return None
