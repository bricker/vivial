import unittest.mock
from typing import Any, override

from google.maps.places import PhotoMedia, Place, SearchNearbyResponse
from google.maps.routing import ComputeRoutesResponse, Route
from google.protobuf.duration_pb2 import Duration

from eave.core.lib.google_places import GeocodeGeometry, GeocodeLocation, GeocodeResult
from eave.stdlib.test_helpers.mocking_mixin import MockingMixin
from eave.stdlib.test_helpers.random_data_mixin import RandomDataMixin


class GooglePlacesMocksMixin(MockingMixin, RandomDataMixin):
    mock_google_place: Place  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_google_places_photo_media: PhotoMedia  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_compute_routes_response: ComputeRoutesResponse  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_maps_geocoding_response: list[GeocodeResult]  # pyright: ignore [reportUninitializedInstanceVariable]

    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._add_google_places_client_mocks()
        self._add_google_routes_client_mocks()
        self._add_google_maps_client_mocks()

    def _add_google_places_client_mocks(self) -> None:
        self.mock_google_place = Place(
            id=self.anystr("Place.id"),
        )

        async def _mock_google_places_search_nearby(*args, **kwargs) -> SearchNearbyResponse:
            return SearchNearbyResponse(
                places=[self.mock_google_place],
            )

        self.patch(
            name="google places searchNearby",
            patch=unittest.mock.patch(
                "google.maps.places_v1.services.places.async_client.PlacesAsyncClient.search_nearby"
            ),
            side_effect=_mock_google_places_search_nearby,
        )

        async def _mock_google_places_get_place(*args, **kwargs) -> Place:
            return self.mock_google_place

        self.patch(
            name="PlacesAsyncClient.get_place",
            patch=unittest.mock.patch("google.maps.places_v1.services.places.async_client.PlacesAsyncClient.get_place"),
            side_effect=_mock_google_places_get_place,
        )

        self.mock_google_places_photo_media = PhotoMedia(
            name=self.anystr("PhotoMedia.name"),
            photo_uri=self.anyurl("PhotoMedia.photo_uri"),
        )

        async def _mock_google_places_get_photo_media(*args: Any, **kwargs: Any) -> PhotoMedia:
            return self.mock_google_places_photo_media

        self.patch(
            name="PlacesAsyncClient.get_photo_media",
            patch=unittest.mock.patch(
                "google.maps.places_v1.services.places.async_client.PlacesAsyncClient.get_photo_media"
            ),
            side_effect=_mock_google_places_get_photo_media,
        )

    def _add_google_routes_client_mocks(self) -> None:
        self.mock_compute_routes_response = ComputeRoutesResponse(
            routes=[
                Route(
                    duration=Duration(
                        seconds=self.anyint(),
                    ),
                ),
            ],
        )

        async def _mock_google_routes_compute_routes(*args, **kwargs) -> ComputeRoutesResponse:
            return self.mock_compute_routes_response

        self.patch(
            name="google routes compute_routes",
            patch=unittest.mock.patch("google.maps.routing.RoutesAsyncClient.compute_routes"),
            side_effect=_mock_google_routes_compute_routes,
        )

    def _add_google_maps_client_mocks(self) -> None:
        self.mock_maps_geocoding_response = [
            GeocodeResult(
                place_id=self.anystr(),
                geometry=GeocodeGeometry(
                    location=GeocodeLocation(
                        lat=self.anylatitude(),
                        lng=self.anylongitude(),
                    ),
                ),
            ),
        ]

        async def _mock_google_maps_geocode(*args, **kwargs) -> list[GeocodeResult]:
            return self.mock_maps_geocoding_response

        self.patch(
            name="google maps geocode",
            patch=unittest.mock.patch("googlemaps.geocoding.geocode"),
            side_effect=_mock_google_maps_geocode,
        )
