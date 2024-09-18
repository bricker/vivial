import os

from eave.collectors.core.config import (
    EaveCredentials,
    eave_ingest_base_url,
    eave_env,
    is_development,
    queue_flush_frequency_seconds,
    queue_maxsize,
)

from .base import BaseTestCase


class ConfigTest(BaseTestCase):
    async def test_eave_ingest_base_url(self) -> None:
        if "EAVE_INGEST_BASE_URL" in os.environ:
            del os.environ["EAVE_INGEST_BASE_URL"]
        assert eave_ingest_base_url() == "https://api.eave.fyi"

        os.environ["EAVE_INGEST_BASE_URL"] = "https://eave.test"
        assert eave_ingest_base_url() == "https://eave.test"

    async def test_eave_credentials_missing(self) -> None:
        del os.environ["EAVE_CREDENTIALS"]
        creds = EaveCredentials.from_env()
        assert creds is None

    async def test_eave_credentials_invalid(self) -> None:
        os.environ["EAVE_CREDENTIALS"] = "abc"
        creds = EaveCredentials.from_env()
        assert creds is None

    async def test_eave_credentials_valid(self) -> None:
        os.environ["EAVE_CREDENTIALS"] = "abc:123"
        creds = EaveCredentials.from_env()
        assert creds is not None
        assert creds.client_id == "abc"
        assert creds.client_secret == "123"

    async def test_eave_credentials_combined(self) -> None:
        os.environ["EAVE_CREDENTIALS"] = "abc:123"
        creds = EaveCredentials.from_env()
        assert creds is not None
        assert creds.combined == "abc:123"
        assert str(creds) == "abc:123"

    async def test_eave_credentials_to_headers(self) -> None:
        os.environ["EAVE_CREDENTIALS"] = "abc:123"
        creds = EaveCredentials.from_env()
        assert creds is not None
        assert creds.to_headers == {
            "eave-client-id": "abc",
            "eave-client-secret": "123",
        }

    async def test_eave_env(self) -> None:
        del os.environ["EAVE_ENV"]
        assert eave_env() == "production"
        assert is_development() is False
        assert queue_maxsize() == 1
        assert queue_flush_frequency_seconds() == 30

        os.environ["EAVE_ENV"] = "development"
        assert eave_env() == "development"
        assert is_development() is True
        assert queue_maxsize() == 1
        assert queue_flush_frequency_seconds() == 30
