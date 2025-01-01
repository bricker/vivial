from eave.core.lib.address import Address
from eave.core.shared.geo import GeoPoint
from eave.stdlib.test_helpers.random_data_mixin import RandomDataMixin


class RandomInstanceMixin(RandomDataMixin):
    def anyaddress(self, name: str | None = None) -> Address:
        name = self._make_testdata_name(name)

        data = Address(
            address1=self.anystr(),
            address2=self.anystr(),
            city=self.anystr(),
            country=self.anystr(),
            state=self.anyusstate(),
            zip_code=self.anydigits(length=5),
        )

        self.testdata[name] = data
        return self.getaddress(name)

    def getaddress(self, name: str) -> Address:
        return self.testdata[name]

    def anycoordinates(self, name: str | None = None) -> GeoPoint:
        name = self._make_testdata_name(name)

        data = GeoPoint(
            lat=self.anylatitude(),
            lon=self.anylongitude(),
        )

        self.testdata[name] = data
        return self.getcoordinates(name)

    def getcoordinates(self, name: str) -> GeoPoint:
        return self.testdata[name]
