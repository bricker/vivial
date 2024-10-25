import logging
from collections.abc import Mapping
from enum import StrEnum
from http import HTTPMethod
from typing import Any, TypedDict
import json

import aiohttp


# TODO: Note about official google maps SDK.



class GooglePlacesClient:
    base_url = "https://places.googleapis.com/v1"
    api_key: str

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def search_nearby(self, *, types: list[str], lat: float, lon: float, radius: float) -> None:
        """https://developers.google.com/maps/documentation/places/web-service/nearby-search"""

        print("Searching nearby...")

        response = await self.make_request()
        j = await response.json()

        print(j)
        # return j

    async def make_request(
        self,
    ) -> aiohttp.ClientResponse:


        async with aiohttp.ClientSession(raise_for_status=True) as session:
            response = await session.request(
                method=HTTPMethod.POST,
                url="https://places.googleapis.com/v1/places:searchNearby",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-FieldMask": "places.displayName"
                },
                data=json.dumps({
                    "includedTypes": [
                        "sushi_restaurant"
                    ],
                    "maxResultCount": 10,
                    "locationRestriction": {
                        "circle": {
                        "center": {
                            "latitude": 37.7937,
                            "longitude": -122.3965
                        },
                        "radius": 500
                        }
                    }
                }),
            )

            # Consume the body while the session is still open
            await response.read()
        return response

