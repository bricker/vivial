import os
from dataclasses import dataclass
from typing import Self, TypedDict

from eave.collectors.core.logging import EAVE_LOGGER


def eave_api_base_url() -> str:
    return os.getenv("EAVE_API_BASE_URL_PUBLIC", "https://api.eave.fyi")


EaveAuthHeaders = TypedDict(
    "EaveAuthHeaders",
    {
        "eave-client-id": str,
        "eave-client-secret": str,
    },
)


@dataclass(kw_only=True, frozen=True)
class EaveCredentials:
    @classmethod
    def from_env(cls) -> Self | None:
        creds_str = os.getenv("EAVE_CREDENTIALS")
        if not creds_str:
            return None

        parts = creds_str.split(":")

        if len(parts) != 2:
            EAVE_LOGGER.warning('invalid credentials format. Expected format: "client_id:client_secret"')
            return None

        return cls(
            client_id=parts[0],
            client_secret=parts[1],
        )

    client_id: str
    client_secret: str

    @property
    def combined(self) -> str:
        return f"{self.client_id}:{self.client_secret}"

    @property
    def to_headers(self) -> EaveAuthHeaders:
        return {
            "eave-client-id": self.client_id,
            "eave-client-secret": self.client_secret,
        }

    def __str__(self) -> str:
        return self.combined


def eave_env() -> str:
    return os.getenv("EAVE_ENV", default="production")


def is_development() -> bool:
    return eave_env() == "development"


def telemetry_disabled() -> bool:
    return os.getenv("EAVE_DISABLE_TELEMETRY") is not None


def queue_maxsize() -> int:
    if is_development():
        return 1
    else:
        return 1  # TODO: make this >0


def queue_flush_frequency_seconds() -> int:
    if is_development():
        return 30
    else:
        return 30
