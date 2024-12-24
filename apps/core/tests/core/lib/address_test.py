import dataclasses
import json

from eave.core.lib.address import Address, format_address

from ..base import BaseTestCase


class TestAddressDataclass(BaseTestCase):
    async def test_address_serializable(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=self.anyalpha("address2"),
            city=self.anyalpha("city"),
            state=self.anyusstate("state"),
            zip_code=self.anydigits("zip_code", length=5),
            country="US",
        )

        j = json.dumps(dataclasses.asdict(address))
        p = json.loads(j)
        assert p["address1"] == self.getalpha("address1")
        assert p["address2"] == self.getalpha("address2")
        assert p["city"] == self.getalpha("city")
        assert p["state"] == self.getusstate("state")
        assert p["zip_code"] == self.getdigits("zip_code")
        assert p["country"] == "US"

    async def test_address_formatted(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=self.anyalpha("address2"),
            city=self.anyalpha("city"),
            state=self.anyusstate("state"),
            zip_code=self.anydigits("zip", length=5),
            country="US",
        )

        assert (
            format_address(address, singleline=False)
            == f"{self.getalpha("address1")}, {self.getalpha("address2")}\n{self.getalpha("city")}, {self.getusstate("state")}, {self.getdigits("zip")}"
        )
        assert (
            format_address(address, singleline=True)
            == f"{self.getalpha("address1")}, {self.getalpha("address2")}, {self.getalpha("city")}, {self.getusstate("state")}, {self.getdigits("zip")}"
        )

    async def test_address_formatted_none(self) -> None:
        address = Address(
            address1=None,
            address2=None,
            city=None,
            state=None,
            zip_code=None,
            country="US",
        )

        assert format_address(address, singleline=False) == ""
        assert format_address(address, singleline=True) == ""

    async def test_address_formatted_empty_strings(self) -> None:
        address = Address(
            address1="",
            address2="",
            city="",
            state="",
            zip_code="",
            country="US",
        )

        assert format_address(address, singleline=False) == ""
        assert format_address(address, singleline=True) == ""

    async def test_address_formatted_some_fields_0(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=None,
            city=self.anyalpha("city"),
            state=self.anyusstate("state"),
            zip_code=self.anydigits("zip"),
            country="US",
        )

        assert (
            format_address(address, singleline=False)
            == f"{self.getalpha("address1")}\n{self.getalpha("city")}, {self.getusstate("state")}, {self.getdigits("zip")}"
        )
        assert (
            format_address(address, singleline=True)
            == f"{self.getalpha("address1")}, {self.getalpha("city")}, {self.getusstate("state")}, {self.getdigits("zip")}"
        )

    async def test_address_formatted_some_fields_1(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=None,
            city=None,
            state=self.anyusstate("state"),
            zip_code=self.anydigits("zip"),
            country="US",
        )

        assert (
            format_address(address, singleline=False)
            == f"{self.getalpha("address1")}\n{self.getusstate("state")}, {self.getdigits("zip")}"
        )
        assert (
            format_address(address, singleline=True)
            == f"{self.getalpha("address1")}, {self.getusstate("state")}, {self.getdigits("zip")}"
        )

    async def test_address_formatted_some_fields_2(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=None,
            city=None,
            state=None,
            zip_code=self.anydigits("zip"),
            country="US",
        )

        assert format_address(address, singleline=False) == f"{self.getalpha("address1")}\n{self.getdigits("zip")}"
        assert format_address(address, singleline=True) == f"{self.getalpha("address1")}, {self.getdigits("zip")}"

    async def test_address_formatted_some_fields_3(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=None,
            city=self.anyalpha("city"),
            state=None,
            zip_code=self.anydigits("zip"),
            country="US",
        )

        assert (
            format_address(address, singleline=False)
            == f"{self.getalpha("address1")}\n{self.getalpha("city")}, {self.getdigits("zip")}"
        )
        assert (
            format_address(address, singleline=True)
            == f"{self.getalpha("address1")}, {self.getalpha("city")}, {self.getdigits("zip")}"
        )

    async def test_address_formatted_some_fields_4(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=None,
            city=None,
            state=self.anyusstate("state"),
            zip_code=None,
            country="US",
        )

        assert format_address(address, singleline=False) == f"{self.getalpha("address1")}\n{self.getusstate("state")}"
        assert format_address(address, singleline=True) == f"{self.getalpha("address1")}, {self.getusstate("state")}"

    async def test_address_formatted_some_fields_5(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=self.anyalpha("address2"),
            city=None,
            state=None,
            zip_code=None,
            country="US",
        )

        assert format_address(address, singleline=False) == f"{self.getalpha("address1")}, {self.getalpha("address2")}"
        assert format_address(address, singleline=True) == f"{self.getalpha("address1")}, {self.getalpha("address2")}"

    async def test_address_formatted_some_fields_6(self) -> None:
        address = Address(
            address1=self.anyalpha("address1"),
            address2=self.anyalpha("address2"),
            city=self.anyalpha("city"),
            state=None,
            zip_code=None,
            country="US",
        )

        assert (
            format_address(address, singleline=False)
            == f"{self.getalpha("address1")}, {self.getalpha("address2")}\n{self.getalpha("city")}"
        )
        assert (
            format_address(address, singleline=True)
            == f"{self.getalpha("address1")}, {self.getalpha("address2")}, {self.getalpha("city")}"
        )
