import hashlib
import json
import math
import random
import time
import uuid
import zoneinfo
from datetime import datetime, timedelta, tzinfo
from typing import Any, Literal, override
from zoneinfo import ZoneInfo

from eave.stdlib.test_helpers.base_mixin import BaseMixin
from eave.stdlib.time import ONE_YEAR_IN_SECONDS
from eave.stdlib.typing import NOT_SET, JsonObject

# This should only be used in testing - it is inefficient
_AVAILABLE_TIMEZONES = list(zoneinfo.available_timezones())
_ALPHAS = "abcdefghijklmnopqrstuvwxyz" * 100


class RandomDataMixin(BaseMixin):
    testdata: dict[str, Any]

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.testdata = {}

    @override
    async def cleanup(self) -> None:
        await super().cleanup()
        self.testdata.clear()

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
        self, name: str | None = None, *, deterministic_keys: bool = False, minlength: int = 0, maxlength: int = 3
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

        assert min is not None and max is not None  # This is for the typechecker, it is an impossible case

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
        data = math.floor(
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
