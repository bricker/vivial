import abc
import hashlib
import json
import time
import typing
import urllib.parse
from base64 import b64encode
from dataclasses import dataclass
from uuid import uuid4

from cryptography import fernet

from eave.collectors.core.config import EaveCredentials
from eave.collectors.core.json import JsonScalar, compact_json
from eave.collectors.core.logging import EAVE_CORE_LOGGER

# The cookie prefix MUST match the browser collector
EAVE_COLLECTOR_COOKIE_PREFIX = "_eave."
EAVE_COLLECTOR_ENCRYPTED_COOKIE_PREFIX = f"{EAVE_COLLECTOR_COOKIE_PREFIX}nc."
EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX = f"{EAVE_COLLECTOR_ENCRYPTED_COOKIE_PREFIX}act."
EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME = "account_id"
EAVE_COLLECTOR_SESS_COOKIE_NAME = "session"
EAVE_COLLECTOR_VISITOR_COOKIE_NAME = "visitor_id"

STORAGE_ATTR = "_eave_corr_ctx"


def corr_ctx_symmetric_encryption_key(credentials: str) -> bytes:
    return b64encode(hashlib.sha256(bytes(credentials, "utf-8")).digest())


class CorrCtxStorage:
    received: dict[str, JsonScalar]
    updated: dict[str, JsonScalar]

    def __init__(self) -> None:
        self.received = {}
        self.updated = {}

    def get(self, key: str, *, prefix: str = EAVE_COLLECTOR_COOKIE_PREFIX) -> JsonScalar | None:
        """Get a value from either storage"""

        finalkey = f"{prefix}{key}"
        updated_value = self.updated.get(finalkey)
        if updated_value is not None:
            return updated_value
        return self.received.get(finalkey)

    def set(
        self, key: str, value: JsonScalar | None, *, prefix: str = EAVE_COLLECTOR_COOKIE_PREFIX, encrypt: bool = True
    ) -> None:
        """Set a value in updated_context storage"""

        if value is None:
            return None

        if not encrypt:
            finalkey = f"{prefix}{key}"
            self.updated[finalkey] = value
            return

        creds = EaveCredentials.from_env()
        if not creds:
            EAVE_CORE_LOGGER.warning("Credentials not set; cannot encrypt. Value was not set.")
            return None

        try:
            attr = CorrelationContextAttr(key=key, value=value)
            encryption_key = corr_ctx_symmetric_encryption_key(creds.combined)
            encrypted_attr = attr.to_encrypted(encryption_key=encryption_key)
            if encrypted_attr is None:
                EAVE_CORE_LOGGER.warning("Encryption failed; Value was not set.")
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
            EAVE_CORE_LOGGER.exception(e)
            return None

    def merged(self) -> dict[str, JsonScalar]:
        """merge received and updated values together"""

        return {**self.received, **self.updated}

    def to_json(self) -> str:
        """Convert entirety of storage to JSON string"""

        return json.dumps(self.merged())

    def updated_values_cookies(self) -> list[str]:
        """
        Convert updated_context store to URL encoded cookie strings.

        Only the updated_context values are converted to prevent
        overwriting potentially changed browser cookies with stale values.
        """

        # URL encode the cookie value
        return [f"{key}={_cookify(value)}; SameSite=Lax; Secure; Path=/" for key, value in self.updated.items()]

    def load_from_cookies(self, cookies: dict[str, str]) -> None:
        """Populate received_context storage from EAVE_COLLECTOR_COOKIE_PREFIX prefixed cookies"""
        if len(self.merged()) > 0:
            EAVE_CORE_LOGGER.warning("Loaded correlation context from cookies more than once")

        eave_cookies = [(k, v) for k, v in cookies.items() if k.startswith(EAVE_COLLECTOR_COOKIE_PREFIX)]

        # make sure all server events have session + visitor_id in context;
        # create new values for them if necessary to send back to client.
        cookie_names = [cookie_name for cookie_name, _ in eave_cookies]
        if f"{EAVE_COLLECTOR_COOKIE_PREFIX}{EAVE_COLLECTOR_SESS_COOKIE_NAME}" not in cookie_names:
            self.set(
                key=EAVE_COLLECTOR_SESS_COOKIE_NAME,
                # NOTE: the shape of this cookie value MUST match the SessionProperties type in the browser-js collector
                value=json.dumps(
                    {
                        "id": str(uuid4()),
                        "start_timestamp": time.time(),
                    }
                ),
                encrypt=False,
            )
        if f"{EAVE_COLLECTOR_COOKIE_PREFIX}{EAVE_COLLECTOR_VISITOR_COOKIE_NAME}" not in cookie_names:
            self.set(key=EAVE_COLLECTOR_VISITOR_COOKIE_NAME, value=str(uuid4()), encrypt=False)

        # save all eave cookies into ctx
        for cookie_name, value in eave_cookies:
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

    def get(self, key: str, *, prefix: str = EAVE_COLLECTOR_COOKIE_PREFIX) -> JsonScalar | None:
        """Get a value from either storage"""

        storage = self.get_storage()
        if not storage:
            return None
        return storage.get(key=key, prefix=prefix)

    def set(
        self, key: str, value: JsonScalar | None, *, prefix: str = EAVE_COLLECTOR_COOKIE_PREFIX, encrypt: bool = True
    ) -> None:
        """Set a value in updated_context storage"""

        storage = self.get_storage()
        if not storage:
            return
        storage.set(key=key, value=value, prefix=prefix, encrypt=encrypt)

    def to_dict(self) -> dict[str, JsonScalar]:
        """Convert entirety of storage to dict"""

        storage = self.get_storage()
        if not storage:
            return {}
        return storage.merged()

    def to_json(self) -> str:
        """Convert entirety of storage to JSON string"""

        storage = self.get_storage()
        if not storage:
            return "{}"
        return storage.to_json()

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
            EAVE_CORE_LOGGER.exception(e)
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
            EAVE_CORE_LOGGER.exception(e)
            return None
