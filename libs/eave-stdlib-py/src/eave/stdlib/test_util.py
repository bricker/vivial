import base64
from datetime import datetime, timedelta
import json
import uuid
import random
from typing import Any, Literal, TypeVar, Optional
import unittest.mock

from google.cloud.secretmanager import AccessSecretVersionRequest, AccessSecretVersionResponse, SecretPayload
from eave.stdlib.checksum import generate_checksum
import eave.stdlib.util
import eave.stdlib.exceptions
import eave.stdlib.signing
from eave.stdlib.typing import JsonObject
from eave.stdlib.config import SHARED_CONFIG

T = TypeVar("T")
M = TypeVar("M", bound=unittest.mock.Mock)


class UtilityBaseTestCase(unittest.IsolatedAsyncioTestCase):
    testdata: dict[str, Any]
    active_mocks: dict[str, unittest.mock.Mock]
    _active_patches: dict[str, unittest.mock._patch]
    _active_patched_dicts: dict[str, unittest.mock._patch_dict]

    def __init__(self, methodName: str = "runTest") -> None:  # type: ignore[no-untyped-def]
        super().__init__(methodName)

        self.testdata = {}
        self.active_mocks = {}
        self._active_patches = {}
        self._active_patched_dicts = {}

        self.addAsyncCleanup(self.cleanup)

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        SHARED_CONFIG.reset_cached_properties()
        self.mock_google_services()
        self.mock_slack_client()
        self.mock_signing()
        self.mock_analytics()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    async def cleanup(self) -> None:
        self.stop_all_patches()
        self.testdata.clear()
        self.active_mocks.clear()
        self._active_patches.clear()
        self._active_patched_dicts.clear()

    @staticmethod
    async def mock_coroutine(value: T) -> T:
        return value

    @staticmethod
    def unwrap(value: Optional[T]) -> T:
        return eave.stdlib.util.unwrap(value)

    def anydatetime(
        self,
        name: Optional[str] = None,
        offset: Optional[int] = None,
        future: Optional[Literal[True]] = None,
        past: Optional[Literal[True]] = None,
    ) -> datetime:
        """
        - offset, future, and past arguments are mutually exclusive. Passing more than one is undefined behavior.
        - offset specified in positive or negative seconds.
        - if future or past are given, the datetime will be a random number of seconds in that direction, within a year of the current date.
        - if no arguments are given, the datetime will be a random number of seconds in a random direction, within a year of the current date.
        """
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            oneyear = 60 * 60 * 24 * 365
            if not offset:
                if not future and not past:
                    offset = random.randint(-oneyear, oneyear)
                else:
                    offset = random.randint(1, oneyear)
                    if past:
                        offset = -offset

            delta = timedelta(seconds=offset)

            data = datetime.utcnow() + delta
            self.testdata[name] = data

        value: datetime = self.testdata[name]
        return value

    _increment = -1  # so that the first increment returns 0

    def increment(self) -> int:
        self._increment += 1
        return self._increment

    def anyurl(self, name: Optional[str] = None) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = f"https://{name}.{uuid.uuid4()}.com/{uuid.uuid4()}"
            self.testdata[name] = data

        value: str = self.testdata[name]
        return value

    def geturl(self, name: str) -> str:
        return self.testdata[name]

    def anypath(self, name: Optional[str] = None) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = f"/{name}/{uuid.uuid4()}"
            self.testdata[name] = data

        value: str = self.testdata[name]
        return value

    def getpath(self, name: str) -> str:
        return self.testdata[name]

    def anystr_b64(self, name: Optional[str] = None, urlsafe: bool = False) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = str(uuid.uuid4())
            new_value = f"{name}:{data}"
            if urlsafe:
                new_value = base64.urlsafe_b64encode(new_value.encode()).decode()
            else:
                new_value = base64.b64encode(new_value.encode()).decode()

            self.testdata[name] = new_value

        return self.testdata[name]

    def anystr(self, name: Optional[str] = None) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = str(uuid.uuid4())
            new_value = f"{name}:{data}"
            self.testdata[name] = new_value

        return self.testdata[name]

    def anystring(self, name: Optional[str] = None) -> str:
        """
        DEPRECATED, use anystr
        """
        return self.anystr(name=name)

    def getstr_b64(self, name: str, urlsafe: bool = False) -> str:
        v = self.testdata[name]

        if urlsafe:
            return base64.urlsafe_b64decode(v).decode()
        else:
            return base64.b64decode(v).decode()

    def getstr(self, name: str) -> str:
        return self.testdata[name]

    def b64encode(self, value: str, urlsafe: bool = False) -> str:
        b = value.encode()
        if urlsafe:
            return base64.urlsafe_b64encode(b).decode()
        else:
            return base64.b64decode(b).decode()

    def b64decode(self, value: str, urlsafe: bool = False) -> str:
        if urlsafe:
            return base64.urlsafe_b64decode(value).decode()
        else:
            return base64.b64decode(value).decode()

    def anyjson(self, name: Optional[str] = None) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = json.dumps({f"{name}:{uuid.uuid4()}": f"{name}:{uuid.uuid4()}" for _ in range(3)})
            self.testdata[name] = data

        value: str = self.testdata[name]
        return value

    def getjson(self, name: str) -> str:
        return self.testdata[name]

    def anydict(self, name: Optional[str] = None, deterministic_keys: bool = False) -> JsonObject:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            if deterministic_keys:
                data: JsonObject = {f"{name}:{i}": f"{name}:{uuid.uuid4()}" for i in range(3)}
            else:
                data: JsonObject = {f"{name}:{uuid.uuid4()}": f"{name}:{uuid.uuid4()}" for _ in range(3)}

            self.testdata[name] = data

        value: JsonObject = self.testdata[name]
        return value

    def getdict(self, name: str) -> JsonObject:
        return self.testdata[name]

    def anyuuid(self, name: Optional[str] = None) -> uuid.UUID:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = uuid.uuid4()
            self.testdata[name] = data

        value: uuid.UUID = self.testdata[name]
        return value

    def getuuid(self, name: str) -> uuid.UUID:
        return self.testdata[name]

    def anyint(self, name: Optional[str] = None) -> int:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            data = random.randint(0, 9999)
            self.testdata[name] = data

        value: int = self.testdata[name]
        return value

    def getint(self, name: str) -> int:
        return self.testdata[name]

    def anybytes(self, name: Optional[str] = None, encoding: str = "utf-8") -> bytes:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            v = uuid.uuid4()
            data = bytes(v.hex, encoding)
            self.testdata[name] = data

        return self.testdata[name]

    def getbytes(self, name: str) -> bytes:
        return self.testdata[name]

    @staticmethod
    def all_same(obj1: object, obj2: object, attrs: Optional[list[str]] = None) -> bool:
        """
        Checks if all attributes `attrs` on objects `obj1` and `obj2` are the same value.
        """
        if not attrs:
            return obj1 == obj2
        else:
            # Using `all` seems like a better way to do this, but I deliberately don't because I want
            # to fully loop through `attrs` to catch an invalid/unset attribute. Globally renaming Python attributes in an IDE
            # doesn't update string references to those attributes, so this is a trade-off where it'll be caught during the tests
            # at runtime instead of during static analysis.
            # all(getattr(obj1, attr) == getattr(obj2, attr) for attr in attrs)

            passing = True
            for attr in attrs:
                a1 = getattr(obj1, attr)
                a2 = getattr(obj2, attr)
                if a1 != a2:
                    passing = False

            return passing

    @staticmethod
    def all_different(obj1: object, obj2: object, attrs: Optional[list[str]] = None) -> bool:
        """
        Reciprical of `all_same`: Checks if all attributes `attrs` on objects `obj1` and `obj2` are a different value.
        This is not the same as `not all_same(...)`; that would pass if _any_ of the attributes were different,
        but we want to check if _all_ of the attributes are different, which is what this function does.
        """
        if not attrs:
            return obj1 != obj2
        else:
            passing = True
            for attr in attrs:
                a1 = getattr(obj1, attr)
                a2 = getattr(obj2, attr)
                if a1 == a2:
                    passing = False

            return passing

    def mock_google_services(self) -> None:
        # def _get_runtimeconfig(name: str) -> str:
        #     v: str = os.getenv(name, f"not mocked: {name}")
        #     return v

        def _access_secret_version(
            request: Optional[AccessSecretVersionRequest | dict] = None, *, name: Optional[str] = None, **kwargs: Any
        ) -> AccessSecretVersionResponse:
            if isinstance(request, AccessSecretVersionRequest):
                resolved_name = request.name
            elif isinstance(request, dict) and "name" in request:
                resolved_name = request["name"]
            elif name:
                resolved_name = name
            else:
                raise ValueError("bad name")

            data = self.anybytes(f"secret:{resolved_name}")
            data_crc32 = generate_checksum(data)

            return AccessSecretVersionResponse(
                name=resolved_name,
                payload=SecretPayload(
                    data=data,
                    data_crc32c=data_crc32,
                ),
            )

        self.patch(
            unittest.mock.patch(
                "google.cloud.secretmanager.SecretManagerServiceClient.access_secret_version",
                side_effect=_access_secret_version,
            )
        )

    def mock_slack_client(self) -> None:
        self.patch(name="slack client", patch=unittest.mock.patch("slack_sdk.web.async_client.AsyncWebClient"))

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
        self.patch(
            unittest.mock.patch(
                "eave.stdlib.signing.verify_signature_or_exception", side_effect=_verify_signature_or_exception
            )
        )

    def mock_analytics(self) -> None:
        self.patch(name="analytics", patch=unittest.mock.patch("eave.stdlib.analytics.log_event"))

    def logged_event(self, *args: Any, **kwargs: Any) -> bool:
        mock = self.get_mock("analytics")
        if not mock.called:
            return False

        for call_args in mock.call_args_list:
            args_matched = all([call_args.args[i] == v for i, v in enumerate(args)])
            opaque_params = kwargs.pop("opaque_params", None)
            kwargs_matched = all([call_args.kwargs.get(k) == v for k, v in kwargs.items()])
            if opaque_params:
                opaque_params_matched = all(
                    [call_args.kwargs["opaque_params"].get(k) == v for k, v in opaque_params.items()]
                )
            else:
                opaque_params_matched = True

            if args_matched and kwargs_matched and opaque_params_matched:
                return True

        # No calls matched the given args
        return False

    def patch(self, patch: unittest.mock._patch, name: Optional[str] = None) -> unittest.mock.Mock:
        m = patch.start()
        m._testMethodName = self._testMethodName  # noqa: SLF001

        if name is None:
            if hasattr(patch.target, "__name__"):
                name = f"{patch.target.__name__}.{patch.attribute}"
            else:
                name = f"{patch.target}.{patch.attribute}"

        self._active_patches[name] = patch
        self.active_mocks[name] = m
        return m

    def patch_env(self, values: dict[str, Optional[str]]) -> unittest.mock.Mock:
        m = self.patch_dict(name="env", patch=unittest.mock.patch.dict("os.environ", values))
        return m

    def patch_dict(self, patch: unittest.mock._patch_dict, name: Optional[str] = None) -> unittest.mock.Mock:
        name = name or str(patch.in_dict)
        mock = patch.start()
        self._active_patched_dicts[name] = patch
        self.active_mocks[name] = mock
        return mock

    def get_mock(self, name: str) -> unittest.mock.Mock:
        assert name in self.active_mocks, f"{name} is not patched!"
        return self.active_mocks[name]

    def get_patch(self, name: str) -> unittest.mock._patch:
        assert name in self._active_patches, f"{name} is not patched!"
        return self._active_patches[name]

    def get_patched_dict(self, name: str) -> unittest.mock._patch_dict:
        assert name in self._active_patched_dicts, f"{name} is not patched!"
        return self._active_patched_dicts[name]

    def stop_all_patches(self) -> None:
        unittest.mock.patch.stopall()
