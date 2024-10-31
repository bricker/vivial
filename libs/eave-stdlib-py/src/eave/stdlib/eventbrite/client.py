from collections.abc import Mapping
from enum import StrEnum
from http import HTTPMethod
from typing import Any, TypedDict

import aiohttp

from .models.category import Category, Subcategory
from .models.event import Event
from .models.format import Format
from .models.organizer import Organizer
from .models.question import Question
from .models.shared import MultipartText
from .models.ticket_class import PointOfSale, TicketClass


class OrderBy(StrEnum):
    start_asc = "start_asc"
    start_desc = "start_desc"
    created_asc = "created_asc"
    created_desc = "created_desc"


class GetEventQuery(TypedDict, total=False):
    expand: str
    """included expansions, comma-delimited"""


class ListEventsQuery(TypedDict, total=False):
    expand: str
    """included expansions, comma-delimited"""

    status: str
    """Filter Events by status. Specify multiple status values as a comma delimited string"""

    order_by: OrderBy
    """Sort order of list of Events"""

    start_date: str
    """Filter Events by a specified date range."""

    only_public: bool
    """True = Filter public Events"""


class ListTicketClassesForSaleQuery(TypedDict, total=False):
    pos: PointOfSale
    """Only return ticket classes valid for the given point of sale. If unspecified, online is the default value."""

    code: str
    """
    Only return ticket classes associated with this promo code.
    A promo code may apply discount, unlock hidden tickets, or change availability/remaining quantity of the tickets.
    """

    hold_id: str
    """Only return ticket classes associated with this composite hold id. Requesting user must have event permissions to sell from holds."""


class ListDefaultQuestionsQuery(TypedDict, total=False):
    include_all: bool
    """Return the whole list of canned included or not"""


class ListCustomQuestionsQuery(TypedDict, total=False):
    as_owner: bool
    """Return private Events and fields."""


class EventbriteClient:
    base_url = "https://www.eventbrite.com/api/v3"
    api_key: str

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def get_event_by_id(self, *, event_id: str, query: GetEventQuery | None = None) -> Event:
        """https://www.eventbrite.com/platform/api#/reference/event/retrieve/retrieve-an-event"""

        response = await self.make_request(method=HTTPMethod.GET, path=f"/events/{event_id}", params=query)
        j = await response.json()
        return j

    async def get_event_description(self, *, event_id: str, query: GetEventQuery | None = None) -> MultipartText | None:
        """https://www.eventbrite.com/platform/api#/reference/event-description/retrieve-full-html-description"""

        response = await self.make_request(method=HTTPMethod.GET, path=f"/events/{event_id}/description", params=query)
        j = await response.json()
        return j

    async def get_organizer_by_id(self, *, organizer_id: str) -> Organizer | None:
        """not documented"""

        response = await self.make_request(method=HTTPMethod.GET, path=f"/organizers/{organizer_id}")
        j = await response.json()
        return j

    async def list_events_for_organizer(
        self, *, organizer_id: str, query: ListEventsQuery | None = None
    ) -> list[Event]:
        """not documented"""

        response = await self.make_request(
            method=HTTPMethod.GET, path=f"/organizers/{organizer_id}/events", params=query
        )
        j = await response.json()
        return j["events"]

    async def list_ticket_classes_for_sale_for_event(
        self, *, event_id: str, query: ListTicketClassesForSaleQuery | None = None
    ) -> list[TicketClass]:
        """https://www.eventbrite.com/platform/api#/reference/ticket-class/list/list-ticket-classes-available-for-sale-by-event"""

        response = await self.make_request(
            method=HTTPMethod.GET, path=f"/events/{event_id}/ticket_classes/for_sale", params=query
        )
        j = await response.json()
        return j["ticket_classes"]

    async def list_default_questions_for_event(
        self, *, event_id: str, query: ListDefaultQuestionsQuery | None = None
    ) -> list[Question]:
        """https://www.eventbrite.com/platform/api#/reference/questions/list-default-questions/list-default-questions-by-event"""

        response = await self.make_request(
            method=HTTPMethod.GET, path=f"/events/{event_id}/canned_questions", params=query
        )
        j = await response.json()
        return j["questions"]

    async def list_custom_questions_for_event(
        self, *, event_id: str, query: ListCustomQuestionsQuery | None = None
    ) -> list[Question]:
        """https://www.eventbrite.com/platform/api#/reference/questions/list-custom-questions/list-custom-questions-by-event"""

        response = await self.make_request(method=HTTPMethod.GET, path=f"/events/{event_id}/questions", params=query)
        j = await response.json()
        return j["questions"]

    async def list_formats(self) -> list[Format]:
        """https://www.eventbrite.com/platform/api#/reference/formats/list/list-formats"""

        response = await self.make_request(method=HTTPMethod.GET, path="/formats")
        j = await response.json()
        return j["formats"]

    async def list_categories(self) -> list[Category]:
        """https://www.eventbrite.com/platform/api#/reference/categories/list/list-of-categories"""

        response = await self.make_request(method=HTTPMethod.GET, path="/categories")
        j = await response.json()
        return j["categories"]

    async def list_subcategories(self) -> list[Subcategory]:
        """https://www.eventbrite.com/platform/api#/reference/categories/list/list-of-subcategories"""

        response = await self.make_request(method=HTTPMethod.GET, path="/subcategories")
        j = await response.json()
        return j["subcategories"]

    async def make_request(
        self,
        *,
        method: HTTPMethod,
        path: str,
        json: dict[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            response = await session.request(
                method=method,
                url=f"{self.base_url}/{path}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params=params,
                json=json,
            )

            # Consume the body while the session is still open
            await response.read()

        # TODO: Pagination - https://www.eventbrite.com/platform/api#/introduction/paginated-responses
        # Ideally it is handled automatically, and the list_* client functions return a lazy iterator.
        # j = await response.json()
        # if pagination := j.get("pagination"):
        #     if pagination.get("has_more_items"):
        #         # make another request with continuation_token

        return response
