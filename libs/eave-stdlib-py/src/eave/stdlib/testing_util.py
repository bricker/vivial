# ruff: noqa: FBT001, FBT002, FBT003, S311

import base64
import hashlib
import json
import os
import random
import time
import unittest.mock
import uuid
from datetime import UTC, datetime, timedelta, timezone
from math import floor
from typing import Any, Literal, TypeVar

import google.cloud.dlp_v2
from google.cloud.secretmanager import AccessSecretVersionRequest, AccessSecretVersionResponse, SecretPayload

import eave.stdlib.exceptions
import eave.stdlib.util
from eave.stdlib.checksum import generate_checksum
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LogContext
from eave.stdlib.typing import JsonObject

T = TypeVar("T")
M = TypeVar("M", bound=unittest.mock.Mock)


class UtilityBaseTestCase(unittest.IsolatedAsyncioTestCase):
    testdata: dict[str, Any]
    active_mocks: dict[str, unittest.mock.Mock]
    empty_ctx: LogContext
    _active_patches: dict[str, unittest.mock._patch]
    _active_patched_dicts: dict[str, unittest.mock._patch_dict]

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.testdata = {}
        self.active_mocks = {}
        self._active_patches = {}
        self._active_patched_dicts = {}

        self.addAsyncCleanup(self.cleanup)

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.empty_ctx = LogContext()
        SHARED_CONFIG.reset_cached_properties()
        self.mock_google_services()
        self.mock_slack_client()

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
    def unwrap(value: T | None) -> T:
        return eave.stdlib.util.unwrap(value)

    def anydatetime(
        self,
        name: str | None = None,
        *,
        offset: int | None = None,
        future: Literal[True] | None = None,
        past: Literal[True] | None = None,
        tz: timezone | None = UTC,
        resolution: Literal["seconds", "microseconds"] = "microseconds",
    ) -> datetime:
        """
        - offset, future, and past arguments are mutually exclusive. Passing more than one is undefined behavior.
        - offset specified in positive or negative seconds.
        - if future or past are given, the datetime will be a random number of seconds in that direction, within a year of the current date.
        - if no arguments are given, the datetime will be a random number of seconds in a random direction, within a year of the current date.
        """
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getdatetime() to retrieve it."

        oneyear = 60 * 60 * 24 * 365
        if not offset:
            if not future and not past:
                offset = random.randint(-oneyear, oneyear)
            else:
                offset = random.randint(1, oneyear)
                if past:
                    offset = -offset

        delta = timedelta(seconds=offset)

        data = datetime.now(tz=tz) + delta
        match resolution:
            case "seconds":
                data = data.replace(microsecond=0)
            case _:
                pass

        self.testdata[name] = data
        return self.getdatetime(name)

    def getdatetime(
        self,
        name: str,
    ) -> datetime:
        assert name in self.testdata, f"test value {name} has not been set. Use anydatetime() to set it."
        return self.testdata[name]

    _increment = -1  # so that the first increment returns 0

    def increment(self) -> int:
        self._increment += 1
        return self._increment

    def anyurl(self, name: str | None = None) -> str:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use geturl() to retrieve it."

        data = f"https://{name}.{uuid.uuid4().hex}.com/{uuid.uuid4().hex}"
        self.testdata[name] = data
        return self.geturl(name)

    def geturl(self, name: str) -> str:
        return self.getstr(name)

    def anypath(self, name: str | None = None) -> str:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getpath() to retrieve it."

        data = f"/{name}/{uuid.uuid4().hex}"
        self.testdata[name] = data
        return self.getpath(name)

    def getpath(self, name: str) -> str:
        return self.getstr(name)

    def anystr(self, name: str | None = None, *, staticvalue: str | None = None) -> str:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getstr() to retrieve it."

        if staticvalue is None:
            data = uuid.uuid4().hex
            value = f"{name}:{data}"
        else:
            value = staticvalue

        self.testdata[name] = value
        return self.getstr(name)

    def getstr(self, name: str) -> str:
        assert name in self.testdata, f"test value {name} has not been set. Use anystr(), anyhex(), etc to set it."
        return self.testdata[name]

    def anyjson(self, name: str | None = None, *, length: int = 3) -> str:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getjson() to retrieve it."

        data = json.dumps({f"{name}:{uuid.uuid4().hex}": f"{name}:{uuid.uuid4().hex}" for _ in range(length)})
        self.testdata[name] = data
        return self.getjson(name)

    def getjson(self, name: str) -> str:
        return self.getstr(name)

    def anydict(
        self, name: str | None = None, deterministic_keys: bool = False, *, minlength: int = 0, maxlength: int = 3
    ) -> dict[str, Any]:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getdict() to retrieve it."

        randlen = random.randint(minlength, b=maxlength)
        if deterministic_keys:
            data: JsonObject = {f"{name}:{i}": f"{name}:{uuid.uuid4().hex}" for i in range(randlen)}
        else:
            data: JsonObject = {f"{name}:{uuid.uuid4().hex}": f"{name}:{uuid.uuid4().hex}" for _ in range(randlen)}

        self.testdata[name] = data
        return self.getdict(name)

    def getdict(self, name: str) -> dict[str, Any]:
        assert name in self.testdata, f"test value {name} has not been set. Use anydict() to set it."
        return self.testdata[name]

    def anylist(self, name: str | None = None, *, minlength: int = 0, maxlength: int = 3) -> list[Any]:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getlist() to retrieve it."

        randlen = random.randint(minlength, maxlength)
        data = [uuid.uuid4().hex for _ in range(randlen)]
        self.testdata[name] = data
        return self.getlist(name)

    def getlist(self, name: str) -> list[Any]:
        assert name in self.testdata, f"test value {name} has not been set. Use anylist() to set it."
        return self.testdata[name]

    def anyuuid(self, name: str | None = None) -> uuid.UUID:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getuuid() to retrieve it."

        data = uuid.uuid4()
        self.testdata[name] = data
        return self.getuuid(name)

    def getuuid(self, name: str) -> uuid.UUID:
        assert name in self.testdata, f"test value {name} has not been set. Use anyuuid() to set it."
        return self.testdata[name]

    def anyhex(self, name: str | None = None) -> str:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use gethex() to retrieve it."

        data = uuid.uuid4().hex
        self.testdata[name] = data
        return self.gethex(name)

    def gethex(self, name: str) -> str:
        return self.getstr(name)

    def anyalpha(self, name: str | None = None, *, length: int = 10) -> str:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getalpha() to retrieve it."

        alphas = "abcdefghijklmnopqrstuvwxyz"
        data = "".join(random.sample(alphas, k=length))
        self.testdata[name] = data
        return self.getalpha(name)

    def getalpha(self, name: str) -> str:
        return self.getstr(name)

    def anyint(self, name: str | None = None, *, min: int = 0, max: int = 9999) -> int:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getint() to retrieve it."

        data = random.randint(min, max)
        self.testdata[name] = data
        return self.getint(name)

    def getint(self, name: str) -> int:
        assert name in self.testdata, f"test value {name} has not been set. Use anyint() to set it."
        return self.testdata[name]

    def anyfloat(self, name: str | None = None, *, mag: int = 0, decimals: int | None = None) -> float:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getfloat() to retrieve it."

        data = round(random.random() * (10**mag), decimals)
        self.testdata[name] = data
        return self.getfloat(name)

    def getfloat(self, name: str) -> float:
        assert name in self.testdata, f"test value {name} has not been set. Use anyfloat() to set it."
        return self.testdata[name]

    def anybytes(self, name: str | None = None, encoding: str = "utf-8") -> bytes:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getbytes() to retrieve it."

        data = uuid.uuid4().bytes
        self.testdata[name] = data
        return self.getbytes(name)

    def getbytes(self, name: str) -> bytes:
        assert name in self.testdata, f"test value {name} has not been set. Use anybytes() to set it."
        return self.testdata[name]

    def anytime(self, name: str | None = None) -> float:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use gettime() to retrieve it."

        offset = random.randint(0, 999999)
        data = floor(
            time.time() - offset
        )  # Use floor so we don't have to worry about microsecond discrepancies in tests
        self.testdata[name] = data
        return self.gettime(name)

    def gettime(self, name: str) -> float:
        return self.getfloat(name)

    def anybool(self, name: str | None = None) -> bool:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getbool() to retrieve it."

        data = random.random() > 0.5
        self.testdata[name] = data
        return self.getbool(name)

    def getbool(self, name: str) -> bool:
        assert name in self.testdata, f"test value {name} has not been set. Use anybool() to set it."
        return self.testdata[name]

    def anysha256(self, name: str | None = None) -> bytes:
        if name is None:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} is already in use. Use getsha256() to retrieve it."

        data = hashlib.sha256(uuid.uuid4().bytes).digest()
        self.testdata[name] = data
        return self.getsha256(name)

    def getsha256(self, name: str) -> bytes:
        return self.getbytes(name)

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

    @staticmethod
    def all_same(obj1: object, obj2: object, attrs: list[str] | None = None) -> bool:
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
    def all_different(obj1: object, obj2: object, attrs: list[str] | None = None) -> bool:
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
        def _access_secret_version(
            request: AccessSecretVersionRequest | dict | None = None, *, name: str | None = None, **kwargs: Any
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

        def _deidentify_content(
            request: google.cloud.dlp_v2.DeidentifyContentRequest, *args, **kwargs
        ) -> google.cloud.dlp_v2.DeidentifyContentResponse:
            """
            All this stub method does is return the input data unchanged.
            """
            return google.cloud.dlp_v2.DeidentifyContentResponse(
                item=request.item,
            )

        self.patch(
            name="dlp.deidentify_content",
            patch=unittest.mock.patch(
                "google.cloud.dlp_v2.DlpServiceAsyncClient.deidentify_content",
                side_effect=_deidentify_content,
            ),
        )

    def mock_slack_client(self) -> None:
        self.patch(name="slack client", patch=unittest.mock.patch("slack_sdk.web.async_client.AsyncWebClient"))

    def logged_event(self, *args: Any, **kwargs: Any) -> bool:
        mock = self.get_mock("analytics")
        if not mock.called:
            return False

        for call_args in mock.call_args_list:
            args_matched = all(call_args.args[i] == v for i, v in enumerate(args))
            opaque_params = kwargs.pop("opaque_params", None)
            kwargs_matched = all(call_args.kwargs.get(k) == v for k, v in kwargs.items())
            if opaque_params:
                opaque_params_matched = all(
                    call_args.kwargs["opaque_params"].get(k) == v for k, v in opaque_params.items()
                )
            else:
                opaque_params_matched = True

            if args_matched and kwargs_matched and opaque_params_matched:
                return True

        # No calls matched the given args
        return False

    def patch(self, patch: unittest.mock._patch, name: str | None = None) -> unittest.mock.Mock:
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

    def patch_env(self, values: dict[str, str | None], clear: bool = False) -> unittest.mock.Mock:
        # This method is the way it is so that we can pass in `None` to implicitly delete keys from os.environ.
        # Otherwise, os.environ only accepts string values, and setting an environment variable to an empty string is not the same as removing an environment variable.
        # i.e., an empty value is treated differently than a missing key in many cases.
        if clear:
            newenv: dict[str, str] = {}
        else:
            newenv = os.environ.copy()

        for k, v in values.items():
            if v is None:
                newenv.pop(k, None)
            else:
                newenv[k] = v

        m = self.patch_dict(name="env", patch=unittest.mock.patch.dict("os.environ", newenv, clear=True))
        return m

    def patch_dict(self, patch: unittest.mock._patch_dict, name: str | None = None) -> unittest.mock.Mock:
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

    def stop_patch(self, name: str) -> None:
        assert name in self._active_patches, f"{name} is not patched!"
        self.get_patch(name).stop()

    def stop_all_patches(self) -> None:
        unittest.mock.patch.stopall()
