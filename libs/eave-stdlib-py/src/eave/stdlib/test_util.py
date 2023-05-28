from datetime import datetime, timedelta
import json
import os
import uuid
import random
from typing import Any, Literal, TypeVar, Optional
import unittest.mock
import eave.stdlib.atlassian
import eave.stdlib.signing

T = TypeVar("T")
M = TypeVar("M", bound=unittest.mock.Mock)


class UtilityBaseTestCase(unittest.IsolatedAsyncioTestCase):
    testdata: dict[str, Any] = {}
    active_patches: dict[str, unittest.mock.Mock] = {}

    def __init__(self, methodName="runTest") -> None:  # type: ignore[no-untyped-def]
        super().__init__(methodName)
        self.addAsyncCleanup(self.cleanup)

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.mock_google_services()
        self.mock_slack_client()
        self.mock_signing()
        self.mock_analytics()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    async def cleanup(self) -> None:
        self.stop_all_patches()
        self.testdata.clear()
        self.active_patches.clear()

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

    def anystring(self, name: Optional[str] = None, only_if_exists: bool = False) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            if only_if_exists:
                raise KeyError(f"testdata {name} not set")

            data = str(uuid.uuid4())
            self.testdata[name] = data

        value: str = self.testdata[name]
        return value

    def getstr(self, name: str) -> str:
        return self.anystring(name=name, only_if_exists=True)

    def anyjson(self, name: Optional[str] = None, only_if_exists: bool = False) -> str:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            if only_if_exists:
                raise KeyError(f"testdata {name} not set")

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

    def getjson(self, name: str) -> str:
        return self.anyjson(name=name, only_if_exists=True)

    def anydict(self, name: Optional[str] = None, only_if_exists: bool = False) -> dict[str, str]:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            if only_if_exists:
                raise KeyError(f"testdata {name} not set")

            data = {
                str(uuid.uuid4()): str(uuid.uuid4()),
                str(uuid.uuid4()): str(uuid.uuid4()),
                str(uuid.uuid4()): str(uuid.uuid4()),
            }
            self.testdata[name] = data

        value: dict[str, str] = self.testdata[name]
        return value

    def getdict(self, name: str) -> dict[str, str]:
        return self.anydict(name=name, only_if_exists=True)

    def anyuuid(self, name: Optional[str] = None, only_if_exists: bool = False) -> uuid.UUID:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            if only_if_exists:
                raise KeyError(f"testdata {name} not set")

            data = uuid.uuid4()
            self.testdata[name] = data

        value: uuid.UUID = self.testdata[name]
        return value

    def getuuid(self, name: str) -> uuid.UUID:
        return self.anyuuid(name=name, only_if_exists=True)

    def anyint(self, name: Optional[str] = None, only_if_exists: bool = False) -> int:
        if name is None:
            name = str(uuid.uuid4())

        if name not in self.testdata:
            if only_if_exists:
                raise KeyError(f"testdata {name} not set")

            data = random.randint(0, 9999)
            self.testdata[name] = data

        value: int = self.testdata[name]
        return value

    def getint(self, name: str) -> int:
        return self.anyint(name=name, only_if_exists=True)

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
            # at runtime instead of during static analysts.
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
        def _get_secret(name: str) -> str:
            v: str = os.getenv(name, f"not mocked: {name}")
            return v

        def _get_runtimeconfig(name: str) -> str:
            v: str = os.getenv(name, f"not mocked: {name}")
            return v

        self.patch(unittest.mock.patch("eave.stdlib.config.EaveConfig.get_secret", side_effect=_get_secret))
        self.patch(
            unittest.mock.patch("eave.stdlib.config.EaveConfig.get_runtimeconfig", side_effect=_get_runtimeconfig)
        )

    def mock_slack_client(self) -> None:
        self.patch(
            name="slack client", patch=unittest.mock.patch("slack_sdk.web.async_client.AsyncWebClient", autospec=True)
        )

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
            kwargs_matched = all([call_args.kwargs[k] == v for k, v in kwargs.items()])
            if opaque_params:
                opaque_params_matched = all(
                    [call_args.kwargs["opaque_params"][k] == v for k, v in opaque_params.items()]
                )
            else:
                opaque_params_matched = True

            if args_matched and kwargs_matched and opaque_params_matched:
                return True

        # No calls matched the given args
        return False

    def patch(self, patch: unittest.mock._patch, name: Optional[str] = None) -> unittest.mock.Mock:  # type:ignore
        m = patch.start()
        m._testMethodName = self._testMethodName

        if name is None:
            if hasattr(patch.target, "__name__"):
                name = f"{patch.target.__name__}.{patch.attribute}"
            else:
                name = f"{patch.target}.{patch.attribute}"

        self.active_patches[name] = m
        return m

    def patch_env(self, values: dict[str, Optional[str]]) -> unittest.mock.Mock:
        m = self.patch_dict(name="env", patch=unittest.mock.patch.dict("os.environ", values))
        return m

    def patch_dict(self, patch: unittest.mock._patch_dict, name: Optional[str] = None) -> unittest.mock.Mock:
        name = name or str(patch.in_dict)
        mock = patch.start()
        self.active_patches[name] = mock
        return mock

    def get_mock(self, name: str) -> unittest.mock.Mock:
        assert name in self.active_patches, f"{name} is not patched!"
        return self.active_patches[name]

    def stop_all_patches(self) -> None:
        unittest.mock.patch.stopall()
