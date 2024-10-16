
from dataclasses import dataclass

import aiohttp

# TODO: move
@dataclass
class YelpBusiness:
    id: str
    alias: str
    name: str
    image_url: str
    is_closed: bool
    url: str
    review_count: int
    categories: list # TODO: array of arrays of YelpCategory objects
    # TODO: finish
    

class YelpFusionAPIClient: 
    base_url: str = "https://api.yelp.com/v3"
    api_key: str
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def search(
        self,
        *, 
        location: str, 
        latitude: str,
        longitude: str,
        term: str,
        radius: int,
        categories: list[str],
        locale: str,
        price: list[int],
        open_now: bool,
        open_at: int,
        attributes: list[str],
        sort_by: str,
        device_platform: str,
        reservation_date: str,
        reservation_time: str,
        reservation_covers: int,
        matches_party_size_param: bool,
        limit: int,
        offset: int,
    ) -> list[YelpBusiness]:
    
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                method=aiohttp.hdrs.METH_GET,
                url=f"{self.base_url}/businesses/search",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={
                    "location": location,
                    "term": term,
                    # TODO finish rest       
                }
            )

            # Consume the body while the session is still open
            await response.read()

        json_response = await response.json()
        return [YelpBusiness(**business_json) for business_json in json_response]
