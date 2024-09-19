import os
from dataclasses import dataclass
from typing import Self, TypedDict


def eave_ingest_base_url() -> str:
    return os.getenv("EAVE_INGEST_BASE_URL", "https://api.eave.fyi")


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
    """Logging telemetry disabled"""
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


# NOTE: keep in sync w/ mirror definition eave std lib!
# (until pydantic dep is removed or we decide to have collectors depend on it too)
@dataclass(kw_only=True)
class DataCollectorConfig:
    user_table_name_patterns: list[str]
    primary_key_patterns: list[str]
    foreign_key_patterns: list[str]


# assign the fallback value as the default
remote_config = DataCollectorConfig(
    user_table_name_patterns=[
        r"users?$",
        r"accounts?$",
        r"customers?$",
    ],
    primary_key_patterns=[
        r"^id$",
        r"^uid$",
    ],
    foreign_key_patterns=[
        # We don't want to capture fields that end in "id" but aren't foreign keys, like "kool_aid" or "mermaid".
        # We therefore make an assumption that anything ending in "id" with SOME delimeter is a foreign key.
        r".[_-]id$",  # delimeter = {_, -} Only matches when "id" is lower-case.
        r".I[Dd]$",  # delimeter = capital "I" (eg UserId). This also handles underscores/hyphens when the "I" is capital.
    ],
)
