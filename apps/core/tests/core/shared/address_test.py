from textwrap import dedent
from eave.core.lib.geo import GeoPoint
from eave.core.orm.activity import ActivityOrm
from eave.core.orm.image import ImageOrm
from eave.core.shared.address import Address

from ..base import BaseTestCase


class TestAddressDataclass(BaseTestCase):
    async def test_address_formatted(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=self.anyalpha("address2"),
            city=self.anyalpha("city"),
            state=self.anyusstate("state"),
            zip=self.anydigits("zip", length=5),
            country="US",
        )

        assert address.formatted == dedent(
            f"""{self.getalpha("address1")} {self.getalpha("address2")}
            {self.getalpha("city")}, {self.getusstate("state")} {self.getdigits("zip")}"""
        )

    async def test_address_formatted_none(self) -> None:
        address = Address(
            address1=None,
            address2=None,
            city=None,
            state=None,
            zip=None,
            country="US",
        )

        assert address.formatted == ""

    async def test_address_formatted_empty_strings(self) -> None:
        address = Address(
            address1="",
            address2="",
            city="",
            state="",
            zip="",
            country="US",
        )

        assert address.formatted == ""

    async def test_address_formatted_some_fields(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=None,
            city=self.anyalpha("city"),
            state=self.anyusstate("state"),
            zip=self.anydigits("zip"),
            country="US",
        )

        assert address.formatted == dedent(
            f"""{self.getalpha("address1")}
            {self.getalpha("city")}, {self.getusstate("state")} {self.getdigits("zip")}"""
        )

        address = Address(
            address1=self.anyalpha("address1"),
            address2=None,
            city=None,
            state=self.anyusstate("state"),
            zip=self.anydigits("zip"),
            country="US",
        )

        assert address.formatted == dedent(
            f"""{self.getalpha("address1")}
            {self.getusstate("state")} {self.getdigits("zip")}"""
        )


        address = Address(
            address1=self.anyalpha("address1"),
            address2=None,
            city=None,
            state=self.anyusstate("state"),
            zip=None,
            country="US",
        )

        assert address.formatted == dedent(
            f"""{self.getalpha("address1")}
            {self.getusstate("state")}"""
        )

        address = Address(
            address1=self.anyalpha("address1"),
            address2=self.anyalpha("address2"),
            city=None,
            state=None,
            zip=None,
            country="US",
        )

        assert address.formatted == f"{self.getalpha("address1")} {self.getalpha("address2")}"
