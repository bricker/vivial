# ruff: noqa: FBT001, FBT002, FBT003, S311

import base64
import hashlib
import json
import os
import random
import time
import unittest.mock
import uuid
import zoneinfo
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, tzinfo
from math import floor
from typing import Any, Literal, TypeVar, override
from zoneinfo import ZoneInfo

from google.cloud.kms import (
    CryptoKeyVersion,
    GetCryptoKeyVersionRequest,
    MacSignRequest,
    MacSignResponse,
    MacVerifyRequest,
    MacVerifyResponse,
)
from google.cloud.secretmanager import AccessSecretVersionRequest, AccessSecretVersionResponse, SecretPayload

from eave.core.shared.enums import OutingBudget
import eave.stdlib.http_exceptions
import eave.stdlib.util
from eave.stdlib.checksum import generate_checksum
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.models.logo import Logo
from eave.stdlib.eventbrite.models.shared import Address, CurrencyCost, MultipartText
from eave.stdlib.eventbrite.models.ticket_availability import TicketAvailability
from eave.stdlib.eventbrite.models.ticket_class import TicketClass
from eave.stdlib.eventbrite.models.venue import Venue
from eave.stdlib.time import ONE_YEAR_IN_SECONDS
from eave.stdlib.typing import NOT_SET, JsonObject

T = TypeVar("T")
M = TypeVar("M", bound=unittest.mock.Mock)


# This should only be used in testing - it is inefficient
_AVAILABLE_TIMEZONES = list(zoneinfo.available_timezones())
_ALPHAS = "abcdefghijklmnopqrstuvwxyz" * 100


class UtilityBaseTestCase(unittest.IsolatedAsyncioTestCase):
    testdata: dict[str, Any]
    active_mocks: dict[str, unittest.mock.Mock]
    _active_patches: dict[str, unittest.mock._patch]  # pyright: ignore [reportPrivateUsage, reportMissingTypeArgument]
    _active_patched_dicts: dict[str, unittest.mock._patch_dict]  # pyright: ignore [reportPrivateUsage]

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.testdata = {}
        self.active_mocks = {}
        self._active_patches = {}
        self._active_patched_dicts = {}

        self.addAsyncCleanup(self.cleanup)

    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        SHARED_CONFIG.reset_cached_properties()
        self._add_google_secret_manager_mocks()
        self._add_google_kms_mocks()
        self._add_slack_client_mocks()
        self._add_eventbrite_client_mocks()
        self._add_sendgrid_client_mocks()
        self._add_segment_client_mocks()

    @override
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

    _increment = -1  # so that the first increment returns 0

    def increment(self) -> int:
        self._increment += 1
        return self._increment

    def _get_testdata_value(self, name: str) -> Any:
        assert name in self.testdata, f"test value {name} has not been set."
        return self.testdata[name]

    def _make_testdata_name(self, name: str | None) -> str:
        if not name:
            name = uuid.uuid4().hex

        assert name not in self.testdata, f"test value {name} has already been set. "
        return name

    def anydatetime(
        self,
        name: str | None = None,
        *,
        offset: int | None = None,
        future: Literal[True] | None = None,
        past: Literal[True] | None = None,
        tz: tzinfo | None = NOT_SET,
        resolution: Literal["seconds", "microseconds"] = "microseconds",
    ) -> datetime:
        """
        - offset, future, and past arguments are mutually exclusive. Passing more than one is undefined behavior.
        - offset specified in positive or negative seconds, and applied to the current time, effectively giving a known value.
        - if future or past are given, the datetime will be a random number of seconds in that direction, within a year of the current date.
        - if no arguments are given, the datetime will be a random number of seconds in a random direction, within a year of the current date.
        """
        if tz is NOT_SET:
            tz = ZoneInfo("UTC")

        name = self._make_testdata_name(name)

        if not offset:
            if not future and not past:
                offset = random.randint(-ONE_YEAR_IN_SECONDS, ONE_YEAR_IN_SECONDS)
            else:
                offset = random.randint(1, ONE_YEAR_IN_SECONDS)
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
        return self._get_testdata_value(name)

    def anyurl(self, name: str | None = None) -> str:
        name = self._make_testdata_name(name)

        data = f"https://{name}.{uuid.uuid4().hex}.com/{uuid.uuid4().hex}"
        self.testdata[name] = data
        return self.geturl(name)

    def geturl(self, name: str) -> str:
        return self.getstr(name)

    def anypath(self, name: str | None = None) -> str:
        name = self._make_testdata_name(name)

        data = f"/{name}/{uuid.uuid4().hex}"
        self.testdata[name] = data
        return self.getpath(name)

    def getpath(self, name: str) -> str:
        return self.getstr(name)

    def anystr(self, name: str | None = None, *, staticvalue: str | None = None, length: int | None = None) -> str:
        name = self._make_testdata_name(name)

        if staticvalue is None:
            data = uuid.uuid4().hex
            value = f"{name}:{data}"
        else:
            value = staticvalue

        self.testdata[name] = value
        return self.getstr(name)

    def getstr(self, name: str) -> str:
        return self._get_testdata_value(name)

    def anytimezone(self, name: str | None = None) -> ZoneInfo:
        name = self._make_testdata_name(name)

        tzname = random.choice(_AVAILABLE_TIMEZONES)
        self.testdata[name] = ZoneInfo(tzname)
        return self.gettimezone(name)

    def gettimezone(self, name: str) -> ZoneInfo:
        return self._get_testdata_value(name)

    def anyjson(self, name: str | None = None, *, length: int = 3) -> str:
        name = self._make_testdata_name(name)

        data = json.dumps({f"{name}:{uuid.uuid4().hex}": f"{name}:{uuid.uuid4().hex}" for _ in range(length)})
        self.testdata[name] = data
        return self.getjson(name)

    def getjson(self, name: str) -> str:
        return self.getstr(name)

    def anydict(
        self, name: str | None = None, deterministic_keys: bool = False, *, minlength: int = 0, maxlength: int = 3
    ) -> dict[str, Any]:
        name = self._make_testdata_name(name)

        randlen = random.randint(minlength, b=maxlength)
        if deterministic_keys:
            data: JsonObject = {f"{name}:{i}": f"{name}:{uuid.uuid4().hex}" for i in range(randlen)}
        else:
            data: JsonObject = {f"{name}:{uuid.uuid4().hex}": f"{name}:{uuid.uuid4().hex}" for _ in range(randlen)}

        self.testdata[name] = data
        return self.getdict(name)

    def getdict(self, name: str) -> dict[str, Any]:
        return self._get_testdata_value(name)

    def anylist(self, name: str | None = None, *, minlength: int = 0, maxlength: int = 3) -> list[Any]:
        name = self._make_testdata_name(name)

        randlen = random.randint(minlength, maxlength)
        data = [uuid.uuid4().hex for _ in range(randlen)]
        self.testdata[name] = data
        return self.getlist(name)

    def getlist(self, name: str) -> list[Any]:
        return self._get_testdata_value(name)

    def anyuuid(self, name: str | None = None) -> uuid.UUID:
        name = self._make_testdata_name(name)

        data = uuid.uuid4()
        self.testdata[name] = data
        return self.getuuid(name)

    def getuuid(self, name: str) -> uuid.UUID:
        return self._get_testdata_value(name)

    def anyhex(self, name: str | None = None) -> str:
        name = self._make_testdata_name(name)

        data = uuid.uuid4().hex
        self.testdata[name] = data
        return self.gethex(name)

    def gethex(self, name: str) -> str:
        return self.getstr(name)

    def anydigits(self, name: str | None = None, *, length: int = 5) -> str:
        name = self._make_testdata_name(name)

        digits = "123456789"  # 0 is not included because this was made for zip codes and zip codes don't start with 0.
        data = "".join(random.sample(digits, k=length))
        self.testdata[name] = data
        return self.getdigits(name)

    def getdigits(self, name: str) -> str:
        return self.getstr(name)

    def anyusstate(self, name: str | None = None) -> str:
        name = self._make_testdata_name(name)

        state = random.choice(["CA", "NY", "MA", "CO", "AZ", "NV"])
        self.testdata[name] = state
        return self.getusstate(name)

    def getusstate(self, name: str) -> str:
        return self.getstr(name)

    def anyalpha(self, name: str | None = None, *, length: int = 10) -> str:
        name = self._make_testdata_name(name)

        data = "".join(random.sample(_ALPHAS, k=length))
        self.testdata[name] = data
        return self.getalpha(name)

    def getalpha(self, name: str) -> str:
        return self.getstr(name)

    def anylatitude(self, name: str | None = None) -> float:
        name = self._make_testdata_name(name)

        # Get an int between (-90*10^5,90*10^5), and divide by 10^5 to get a value with 5 decimals of precision
        data = random.randint(-90 * (10**5), 90 * (10**5)) / 10**5
        self.testdata[name] = data
        return self.getlatitude(name=name)

    def getlatitude(self, name: str) -> float:
        return self.getfloat(name)

    def anylongitude(self, name: str | None = None) -> float:
        name = self._make_testdata_name(name)

        # Get an int between (-180*10^5,180*10^5), and divide by 10^5 to get a value with 5 decimals of precision
        data = random.randint(-180 * (10**5), 180 * (10**5)) / 10**5
        self.testdata[name] = data
        return self.getlatitude(name=name)

    def getlongitude(self, name: str) -> float:
        return self.getfloat(name)

    def anyint(self, name: str | None = None, *, min: int | None = None, max: int | None = None) -> int:
        if max is None and min is None:
            min = 0
            max = 10**6

        elif min is not None and max is None:
            max = min + 10**6

        elif max is not None and min is None:
            if max > 0:
                min = 0
            else:
                min = max - 10**6

        assert min is not None and max is not None # This is for the typechecker, it is an impossible case

        name = self._make_testdata_name(name)

        data = random.randint(min, max)
        self.testdata[name] = data
        return self.getint(name)

    def getint(self, name: str) -> int:
        return self._get_testdata_value(name)

    def anyfloat(self, name: str | None = None, *, mag: int = 0, decimals: int | None = 5) -> float:
        name = self._make_testdata_name(name)

        data = round(random.random() * (10**mag), decimals)
        self.testdata[name] = data
        return self.getfloat(name)

    def getfloat(self, name: str) -> float:
        return self._get_testdata_value(name)

    def anybytes(self, name: str | None = None, encoding: str = "utf-8") -> bytes:
        name = self._make_testdata_name(name)

        data = uuid.uuid4().bytes
        self.testdata[name] = data
        return self.getbytes(name)

    def getbytes(self, name: str) -> bytes:
        return self._get_testdata_value(name)

    def anytime(self, name: str | None = None) -> float:
        name = self._make_testdata_name(name)

        offset = random.randint(0, 999999)
        data = floor(
            time.time() - offset
        )  # Use floor so we don't have to worry about microsecond discrepancies in tests
        self.testdata[name] = data
        return self.gettime(name)

    def gettime(self, name: str) -> float:
        return self.getfloat(name)

    def anybool(self, name: str | None = None) -> bool:
        name = self._make_testdata_name(name)

        data = random.random() > 0.5
        self.testdata[name] = data
        return self.getbool(name)

    def getbool(self, name: str) -> bool:
        return self._get_testdata_value(name)

    def anysha256(self, name: str | None = None) -> bytes:
        name = self._make_testdata_name(name)

        data = hashlib.sha256(uuid.uuid4().bytes).digest()
        self.testdata[name] = data
        return self.getsha256(name)

    def getsha256(self, name: str) -> bytes:
        return self.getbytes(name)

    def anyemail(self, name: str | None = None) -> str:
        name = self._make_testdata_name(name)

        data = f"{name}+{uuid.uuid4().hex}@gmail.com"
        self.testdata[name] = data
        return self.getemail(name)

    def getemail(self, name: str) -> str:
        return self.getstr(name)

    def anyphonenumber(self, name: str | None = None) -> str:
        name = self._make_testdata_name(name)

        data = f"({self.anydigits(length=3)})-{self.anydigits(length=3)}-{self.anydigits(length=4)}"
        self.testdata[name] = data
        return self.getphonenumber(name)

    def getphonenumber(self, name: str) -> str:
        return self.getstr(name)

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

    def _add_google_secret_manager_mocks(self) -> None:
        def _access_secret_version(
            request: AccessSecretVersionRequest | dict[str, str] | None = None,
            *,
            name: str | None = None,
            **kwargs: Any,
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

    def _add_google_kms_mocks(self) -> None:
        def _mac_sign(request: MacSignRequest) -> MacSignResponse:
            mac = self.anybytes()
            return MacSignResponse(
                verified_data_crc32c=True,
                name=request.name,
                mac=mac,
                mac_crc32c=generate_checksum(mac),
            )

        self.patch(
            unittest.mock.patch(
                "google.cloud.kms.KeyManagementServiceClient.mac_sign",
                side_effect=_mac_sign,
            )
        )

        def _mac_verify(request: MacVerifyRequest) -> MacVerifyResponse:
            return MacVerifyResponse(
                verified_data_crc32c=True,
                verified_mac_crc32c=True,
                name=request.name,
                success=True,
                verified_success_integrity=True,
            )

        self.patch(
            unittest.mock.patch(
                "google.cloud.kms.KeyManagementServiceClient.mac_verify",
                side_effect=_mac_verify,
            )
        )

        def _get_crypto_key_version(request: GetCryptoKeyVersionRequest) -> CryptoKeyVersion:
            return CryptoKeyVersion(
                name=request.name,
                algorithm=CryptoKeyVersion.CryptoKeyVersionAlgorithm.HMAC_SHA256,
            )

        self.patch(
            unittest.mock.patch(
                "google.cloud.kms.KeyManagementServiceClient.get_crypto_key_version",
                side_effect=_get_crypto_key_version,
            )
        )

    def _add_slack_client_mocks(self) -> None:
        self.patch(
            name="slack client",
            patch=unittest.mock.patch("slack_sdk.web.async_client.AsyncWebClient.chat_postMessage"),
            return_value={},
        )

    def _add_segment_client_mocks(self) -> None:
        def _mocked_segment_track(*args: Any, **kwargs: Any) -> Any:
            pass

        self.patch(
            name="segment.analytics.track",
            patch=unittest.mock.patch("segment.analytics.track"),
            side_effect=_mocked_segment_track,
        )

        def _mocked_segment_identify(*args: Any, **kwargs: Any) -> Any:
            pass

        self.patch(
            name="segment.analytics.identify",
            patch=unittest.mock.patch("segment.analytics.identify"),
            side_effect=_mocked_segment_identify,
        )

    mock_eventbrite_event: Event  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_eventbrite_ticket_class_batch: list[TicketClass]  # pyright: ignore [reportUninitializedInstanceVariable]

    def set_mock_eventbrite_ticket_class_batch(self, *, max_cost_cents: int | None = None, min_cost_cents: int | None = None) -> None:
        if max_cost_cents is not None and min_cost_cents is None:
            if max_cost_cents == 0:
                min_cost_cents = 0
            else:
                min_cost_cents = 1

        self.mock_eventbrite_ticket_class_batch = [
            TicketClass(
                id=self.anydigits(),
                cost=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint(min=min_cost_cents, max=max_cost_cents),
                ),
                fee=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
                tax=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
            )
        ]

    def get_mock_eventbrite_ticket_class_batch_cost(self) -> int:
        # These checks are just for the typechecker
        cost = self.mock_eventbrite_ticket_class_batch[0].get("cost")
        fee = self.mock_eventbrite_ticket_class_batch[0].get("fee")
        tax = self.mock_eventbrite_ticket_class_batch[0].get("tax")
        assert cost and tax and fee

        return cost["value"] + fee["value"] + tax["value"]

    def _add_eventbrite_client_mocks(self) -> None:
        self.mock_eventbrite_event = Event(
            id=self.anydigits("eventbrite.Event.id"),
            name=MultipartText(
                text=self.anystr("eventbrite.Event.name.text"),
                html=self.anystr("eventbrite.Event.name.html"),
            ),
            status=EventStatus.LIVE,
            venue=Venue(
                address=Address(),
                latitude=str(self.anylatitude("eventbrite.Venue.latitude")),
                longitude=str(self.anylongitude("eventbrite.Venue.longitude")),
                name=self.anystr("eventbrite.Venue.name"),
            ),
            ticket_availability=TicketAvailability(
                has_available_tickets=True,
            ),
            logo=Logo(
                id=self.anydigits("eventbrite.Logo.id"),
                url=self.anyurl("eventbrite.Logo.url"),
            ),
            changed=self.anydatetime().isoformat(),
            created=self.anydatetime().isoformat(),
        )

        async def _mocked_eventbrite_get_event_by_id(**kwargs: Any) -> Event:
            return self.mock_eventbrite_event

        self.patch(
            name="eventbrite get_event_by_id",
            patch=unittest.mock.patch("eave.stdlib.eventbrite.client.EventbriteClient.get_event_by_id"),
            side_effect=_mocked_eventbrite_get_event_by_id,
        )

        self.mock_eventbrite_ticket_class_batch = [
            TicketClass(
                id=self.anydigits("eventbrite.TicketClass.0.id"),
                cost=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint("eventbrite.TicketClass.0.cost.value"),
                ),
                fee=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint("eventbrite.TicketClass.0.fee.value"),
                ),
                tax=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint("eventbrite.TicketClass.0.tax.value"),
                ),
            )
        ]

        async def _mocked_eventbrite_list_ticket_classes_for_sale_for_event(
            **kwargs: Any,
        ) -> AsyncIterator[list[TicketClass]]:
            yield self.mock_eventbrite_ticket_class_batch

        self.patch(
            name="EventbriteClient.list_ticket_classes_for_sale_for_event",
            patch=unittest.mock.patch(
                "eave.stdlib.eventbrite.client.EventbriteClient.list_ticket_classes_for_sale_for_event"
            ),
            side_effect=_mocked_eventbrite_list_ticket_classes_for_sale_for_event,
        )

        mock_eventbrite_description = MultipartText(
            text=self.anystr("eventbrite.EventDescription.text"),
            html=self.anystr("eventbrite.EventDescription.html"),
        )

        async def _mocked_eventbrite_get_event_description(**kwargs: Any) -> MultipartText:
            return mock_eventbrite_description

        self.patch(
            name="eventbrite get_event_description",
            patch=unittest.mock.patch("eave.stdlib.eventbrite.client.EventbriteClient.get_event_description"),
            side_effect=_mocked_eventbrite_get_event_description,
        )

    def _add_sendgrid_client_mocks(self) -> None:
        self.patch(
            name="SendGridAPIClient.send",
            patch=unittest.mock.patch(
                "sendgrid.SendGridAPIClient.send",
            ),
        )

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

    def patch(
        self,
        patch: unittest.mock._patch,  # pyright: ignore [reportPrivateUsage, reportMissingTypeArgument]
        name: str | None = None,
        return_value: Any | None = None,
        side_effect: Any | None = None,
    ) -> unittest.mock.Mock:
        m = patch.start()
        m._testMethodName = self._testMethodName  # noqa: SLF001

        if name is None:
            if hasattr(patch.target, "__name__"):
                name = f"{patch.target.__name__}.{patch.attribute}"
            else:
                name = f"{patch.target}.{patch.attribute}"

        if return_value is not None:
            m.return_value = return_value

        if side_effect is not None:
            m.side_effect = side_effect

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

    def patch_dict(self, patch: unittest.mock._patch_dict, name: str | None = None) -> unittest.mock.Mock:  # pyright: ignore [reportPrivateUsage]
        name = name or str(patch.in_dict)
        mock = patch.start()
        self._active_patched_dicts[name] = patch
        self.active_mocks[name] = mock
        return mock

    def get_mock(self, name: str) -> unittest.mock.Mock:
        assert name in self.active_mocks, f"{name} is not patched!"
        return self.active_mocks[name]

    def get_patch(self, name: str) -> unittest.mock._patch:  # pyright: ignore [reportPrivateUsage, reportMissingTypeArgument]
        assert name in self._active_patches, f"{name} is not patched!"
        return self._active_patches[name]

    def get_patched_dict(self, name: str) -> unittest.mock._patch_dict:  # pyright: ignore [reportPrivateUsage]
        assert name in self._active_patched_dicts, f"{name} is not patched!"
        return self._active_patched_dicts[name]

    def stop_patch(self, name: str) -> None:
        assert name in self._active_patches, f"{name} is not patched!"
        self.get_patch(name).stop()

    def stop_all_patches(self) -> None:
        unittest.mock.patch.stopall()
