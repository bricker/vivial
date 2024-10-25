from http import HTTPMethod
from typing import Any
import json
import aiohttp

from .models.place import Place
from .models.rank_preference import RankPreference


# TODO: Note about official google maps SDK.

class GooglePlacesClient:
    base_url = "https://places.googleapis.com/v1/places"
    api_key: str

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def search_nearby(
            self,
            *,
            field_mask: list[str],
            latitude: float,
            longitude: float,
            radius: float,
            included_types: list[str] | None,
            excluded_types: list[str] | None,
            included_primary_types: list[str] | None,
            excluded_primary_types: list[str] | None,
            language_code: str | None,
            max_result_count: int | None,
            rank_preference: RankPreference | None,
            region_code: str | None,
        ) -> list[Place] | None:
        """https://developers.google.com/maps/documentation/places/web-service/nearby-search"""

        payload = {
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": radius
                }
            },
            "includedTypes": included_types,
            "excludedTypes": excluded_types,
            "includedPrimaryTypes": included_primary_types,
            "excludedPrimaryTypes": excluded_primary_types,
            "languageCode": language_code,
            "maxResultCount": max_result_count,
            "rankPreference": rank_preference,
            "regionCode": region_code
        }
        response = await self.make_request(
            method=HTTPMethod.POST,
            path="searchNearby",
            field_mask=field_mask,
            payload=payload
        )
        j = await response.json()
        if places := j.get("places"):
            return places

    async def make_request(
        self,
        *,
        method: HTTPMethod,
        path: str,
        field_mask: list[str],
        payload: Any
    ) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            response = await session.request(
                method=method,
                url=f"{self.base_url}:{path}",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-FieldMask": ",".join(field_mask)
                },
                data=json.dumps(payload),
            )
            await response.read()
        return response
