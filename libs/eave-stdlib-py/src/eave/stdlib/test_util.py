import json
import os
import uuid
import random
from typing import Any, TypeVar, Optional
import unittest.mock
import eave.stdlib.atlassian
import eave.stdlib.signing

T = TypeVar("T")
M = TypeVar("M", bound=unittest.mock.Mock)

class TestUtilityMixin:
    testdata: dict[str, Any] = {}
    active_patches: dict[str, unittest.mock.Mock] = {}
    active_dict_patches: dict[str, Any] = {}

    async def asyncSetUp(self) -> None:
        self.mock_google_services()
        self.mock_slack_client()
        self.mock_signing()

    async def asyncTearDown(self) -> None:
        self.stop_all_patches()

    @staticmethod
    async def mock_coroutine(value: T) -> T:
        return value

    @staticmethod
    def unwrap(value: Optional[T]) -> T:
        assert value is not None
        return value

    def anystring(self, name: Optional[str] = None) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = str(uuid.uuid4())
            self.testdata[name] = data

        value: str = self.testdata[name]
        return value

    def anyjson(self, name: Optional[str] = None) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = json.dumps(
                {
                    str(uuid.uuid4()): str(uuid.uuid4()),
                    str(uuid.uuid4()): str(uuid.uuid4()),
                    str(uuid.uuid4()): str(uuid.uuid4()),
                }
            )
            self.testdata[name] = data

        value: str = self.testdata[name]
        return value

    def anydict(self, name: Optional[str] = None) -> dict[str, str]:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = {
                str(uuid.uuid4()): str(uuid.uuid4()),
                str(uuid.uuid4()): str(uuid.uuid4()),
                str(uuid.uuid4()): str(uuid.uuid4()),
            }
            self.testdata[name] = data

        value: dict[str, str] = self.testdata[name]
        return value

    def anyuuid(self, name: Optional[str] = None) -> uuid.UUID:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = uuid.uuid4()
            self.testdata[name] = data

        value: uuid.UUID = self.testdata[name]
        return value

    def anyint(self, name: Optional[str] = None) -> int:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = random.randint(0, 9999)
            self.testdata[name] = data

        value: int = self.testdata[name]
        return value

    def mock_google_services(self) -> None:
        def _get_secret(name: str) -> str:
            v: str = os.getenv(name, f"not mocked: {name}")
            return v

        def _get_runtimeconfig(name: str) -> str:
            v: str = os.getenv(name, f"not mocked: {name}")
            return v

        self.patch(unittest.mock.patch("eave.stdlib.config.EaveConfig.get_secret", side_effect=_get_secret))
        self.patch(unittest.mock.patch("eave.stdlib.config.EaveConfig.get_runtimeconfig", side_effect=_get_runtimeconfig))

    def mock_slack_client(self) -> None:
        self.patch(unittest.mock.patch("slack_sdk.web.async_client.AsyncWebClient", autospec=True))

    def mock_signing(self) -> None:
        def _sign_b64(signing_key: eave.stdlib.signing.SigningKeyDetails, data: str | bytes) -> str:
            value: str = eave.stdlib.util.b64encode(eave.stdlib.util.sha256hexdigest(data))
            return value

        def _verify_signature_or_exception(
            signing_key: eave.stdlib.signing.SigningKeyDetails, message: str | bytes, signature: str
        ) -> None:
            if signature != eave.stdlib.util.b64encode(eave.stdlib.util.sha256hexdigest(message)):
                raise eave.stdlib.exceptions.InvalidSignatureError()

        self.patch(unittest.mock.patch("eave.stdlib.signing.sign_b64", side_effect=_sign_b64))
        self.patch(unittest.mock.patch("eave.stdlib.signing.verify_signature_or_exception", side_effect=_verify_signature_or_exception))


    def patch(self, patch: unittest.mock._patch) -> unittest.mock.Mock: # type:ignore
        m = patch.start()
        self.active_patches[f"{patch.target.__name__}.{patch.attribute}"] = m
        return m

    def patch_dict(self, patch: unittest.mock._patch_dict) -> Any:
        name = patch.in_dict
        self.active_dict_patches[name] = patch.start()

    def get_mock(self, name: str) -> unittest.mock.Mock:
        assert name in self.active_patches, f"{name} is not patched!"
        return self.active_patches[name]

    def stop_all_patches(self) -> None:
        unittest.mock.patch.stopall()
        self.active_patches.clear()