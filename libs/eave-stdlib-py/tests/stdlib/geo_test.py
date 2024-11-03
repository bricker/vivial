from eave.stdlib.geo import GeoCoordinates

from .base import StdlibBaseTestCase


class GeoTest(StdlibBaseTestCase):
    async def test_geo_coordinates_wkt(self):
        coord = GeoCoordinates(lat="80.123", long="100.123")
        assert coord.wkt == "POINT(100.123 80.123)"
