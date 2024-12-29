import dataclasses
import random
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from functools import wraps
from http import HTTPMethod
from typing import Any, Literal

import aiohttp

from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.eventbrite.models.pagination import Pagination
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import NOT_SET

from .models.category import Category, Subcategory
from .models.event import Event, EventDescription, EventStatus
from .models.format import Format
from .models.organizer import Organizer
from .models.question import Question
from .models.ticket_class import PointOfSale, TicketClass


class OrderBy(StrEnum):
    START_ASC = "start_asc"
    START_DESC = "start_desc"
    CREATED_ASC = "created_asc"
    CREATED_DESC = "created_desc"


@dataclass(kw_only=True)
class GetEventQuery:
    expand: list[Expansion] = NOT_SET
    """included expansions"""

    def compile(self) -> Mapping[str, Any]:
        params: dict[str, Any] = {}

        expand = self.expand
        if expand is NOT_SET:
            expand = list(Expansion)

        params["expand"] = ",".join(expand)

        return params


@dataclass(kw_only=True)
class ShowMoreEventsForOrganizerQuery:
    page_size: int = 100
    page: int
    type: Literal["past", "future"] = "future"

    def compile(self) -> Mapping[str, Any]:
        return dataclasses.asdict(self)


@dataclass(kw_only=True)
class ListEventsQuery:
    expand: list[Expansion] = NOT_SET
    """included expansions"""

    status: EventStatus = NOT_SET
    """Filter Events by status. Specify multiple status values as a comma delimited string"""

    order_by: OrderBy = NOT_SET
    """Sort order of list of Events"""

    start_date: str = NOT_SET
    """Filter Events by a specified date range."""

    only_public: bool = NOT_SET
    """True = Filter public Events"""

    def compile(self) -> Mapping[str, Any]:
        params: dict[str, Any] = {}

        expand = self.expand
        if expand is NOT_SET:
            expand = list(Expansion)

        params["expand"] = ",".join(self.expand)

        if self.status is not NOT_SET:
            params["status"] = self.status.value

        if self.order_by is not NOT_SET:
            params["order_by"] = self.order_by.value

        if self.start_date is not NOT_SET:
            params["start_date"] = self.start_date

        if self.only_public is not NOT_SET:
            params["only_public"] = "true" if self.only_public else "false"

        return params


@dataclass(kw_only=True)
class ListTicketClassesForSaleQuery:
    pos: PointOfSale = NOT_SET
    """Only return ticket classes valid for the given point of sale. If unspecified, online is the default value."""

    code: str = NOT_SET
    """
    Only return ticket classes associated with this promo code.
    A promo code may apply discount, unlock hidden tickets, or change availability/remaining quantity of the tickets.
    """

    hold_id: str = NOT_SET
    """Only return ticket classes associated with this composite hold id. Requesting user must have event permissions to sell from holds."""

    def compile(self) -> Mapping[str, Any]:
        params: dict[str, Any] = {}

        if self.pos is not NOT_SET:
            params["pos"] = self.pos.value

        if self.code is not NOT_SET:
            params["code"] = self.code

        if self.hold_id is not NOT_SET:
            params["hold_id"] = self.hold_id

        return params


@dataclass(kw_only=True)
class ListDefaultQuestionsQuery:
    include_all: bool = NOT_SET
    """Return the whole list of canned included or not"""

    def compile(self) -> Mapping[str, Any]:
        params: dict[str, Any] = {}

        if self.include_all is not NOT_SET:
            params["include_all"] = "true" if self.include_all else "false"

        return params


@dataclass(kw_only=True)
class ListCustomQuestionsQuery:
    as_owner: bool = NOT_SET
    """Return private Events and fields."""

    def compile(self) -> Mapping[str, Any]:
        params: dict[str, Any] = {}

        if self.as_owner is not NOT_SET:
            params["as_owner"] = "true" if self.as_owner else "false"

        return params


def paginated[T, **P](
    data_key: str, data_type: type[T]
) -> Callable[[Callable[P, Awaitable[aiohttp.ClientResponse]]], Callable[P, AsyncIterator[T]]]:
    def decorator(f: Callable[P, Awaitable[aiohttp.ClientResponse]]) -> Callable[P, AsyncIterator[T]]:
        @wraps(f)
        async def _inner(*args: P.args, **kwargs: P.kwargs) -> AsyncIterator[T]:
            ctoken: str | None = None

            # These are here to avoid an infinite loop locking up the whole process.
            # Infinite loop could occur if there is a bug in the pagination logic on either client or server.
            current_iter = 0
            max_iter = 50  # Effectively the maximum number of pages we'll fetch.

            while current_iter < max_iter:
                current_iter += 1

                kwargs["continuation"] = ctoken
                response = await f(*args, **kwargs)
                j = await response.json()
                yield j[data_key]

                # Pagination - https://www.eventbrite.com/platform/api#/introduction/paginated-responses
                pagination: Pagination | None = j.get("pagination")
                if not pagination:
                    break

                has_more_items = pagination.get("has_more_items", False)
                if not has_more_items:
                    break

                ctoken = pagination.get("continuation")
                if not ctoken:
                    break

        return _inner

    return decorator


class EventbriteClient:
    base_url = "https://www.eventbrite.com"

    _api_keys: list[str]
    _current_api_key_idx: int

    def __init__(self, *, api_keys: list[str]) -> None:
        if len(api_keys) == 0:
            raise ValueError("At least one Eventbrite API key must be provided")

        self._api_keys = api_keys
        self._current_api_key_idx = random.randrange(len(api_keys))  # noqa: S311

    async def get_event_by_id(self, *, event_id: str, query: GetEventQuery | None = None) -> Event:
        """https://www.eventbrite.com/platform/api#/reference/event/retrieve/retrieve-an-event"""

        response = await self.make_request(
            method=HTTPMethod.GET, path=f"/api/v3/events/{event_id}", query=query.compile() if query else None
        )
        j = await response.json()
        return j

    async def get_event_description(self, *, event_id: str) -> EventDescription:
        """https://www.eventbrite.com/platform/api#/reference/event-description/retrieve-full-html-description"""

        response = await self.make_request(method=HTTPMethod.GET, path=f"/api/v3/events/{event_id}/description")
        j = await response.json()
        return j

    async def get_organizer_by_id(self, *, organizer_id: str) -> Organizer:
        """not documented"""

        response = await self.make_request(method=HTTPMethod.GET, path=f"/api/v3/organizers/{organizer_id}")
        j = await response.json()
        return j

    @paginated("events", list[Event])
    async def list_events_for_organizer(
        self, *, organizer_id: str, query: ListEventsQuery | None = None, continuation: str | None = None
    ) -> aiohttp.ClientResponse:
        """not documented"""

        response = await self.make_request(
            method=HTTPMethod.GET,
            path=f"/api/v3/organizers/{organizer_id}/events",
            query=query.compile() if query else None,
            continuation=continuation,
        )
        return response

    async def show_more_events_for_organizer(
        self,
        *,
        organizer_id: str,
        query: ShowMoreEventsForOrganizerQuery,
    ) -> aiohttp.ClientResponse:
        """
        not documented
        This is used by the Eventbrite website when "Show More" is clicked.
        It can be used in place of "list_events_for_organizer" in case that endpoint stops working.

        This endpoint returns a "has_next_page" boolean which can be used for pagination.
        It doesn't use the continuation token like the other endpoints.
        """

        response = await self.make_request(
            method=HTTPMethod.GET,
            path=f"/org/{organizer_id}/showmore",  # This endpoint does not have the /api/v3 prefix
            query=query.compile(),
        )
        return response

    @paginated("ticket_classes", list[TicketClass])
    async def list_ticket_classes_for_sale_for_event(
        self, *, event_id: str, query: ListTicketClassesForSaleQuery | None = None, continuation: str | None = None
    ) -> aiohttp.ClientResponse:
        """https://www.eventbrite.com/platform/api#/reference/ticket-class/list/list-ticket-classes-available-for-sale-by-event"""

        response = await self.make_request(
            method=HTTPMethod.GET,
            path=f"/api/v3/events/{event_id}/ticket_classes/for_sale",
            query=query.compile() if query else None,
            continuation=continuation,
        )
        return response

    @paginated("questions", list[Question])
    async def list_default_questions_for_event(
        self, *, event_id: str, query: ListDefaultQuestionsQuery | None = None, continuation: str | None = None
    ) -> aiohttp.ClientResponse:
        """https://www.eventbrite.com/platform/api#/reference/questions/list-default-questions/list-default-questions-by-event"""

        response = await self.make_request(
            method=HTTPMethod.GET,
            path=f"/api/v3/events/{event_id}/canned_questions",
            query=query.compile() if query else None,
            continuation=continuation,
        )
        return response

    @paginated("questions", list[Question])
    async def list_custom_questions_for_event(
        self, *, event_id: str, query: ListCustomQuestionsQuery | None = None, continuation: str | None = None
    ) -> aiohttp.ClientResponse:
        """https://www.eventbrite.com/platform/api#/reference/questions/list-custom-questions/list-custom-questions-by-event"""

        response = await self.make_request(
            method=HTTPMethod.GET,
            path=f"/api/v3/events/{event_id}/questions",
            query=query.compile() if query else None,
            continuation=continuation,
        )
        return response

    async def list_formats(self) -> list[Format]:
        """https://www.eventbrite.com/platform/api#/reference/formats/list/list-formats"""

        response = await self.make_request(method=HTTPMethod.GET, path="/api/v3/formats")
        j = await response.json()
        return j["formats"]

    @paginated("categories", list[Category])
    async def list_categories(self, *, continuation: str | None = None) -> aiohttp.ClientResponse:
        """https://www.eventbrite.com/platform/api#/reference/categories/list/list-of-categories"""

        response = await self.make_request(method=HTTPMethod.GET, path="/api/v3/categories", continuation=continuation)
        return response

    @paginated("subcategories", list[Subcategory])
    async def list_subcategories(self, *, continuation: str | None = None) -> aiohttp.ClientResponse:
        """https://www.eventbrite.com/platform/api#/reference/categories/list/list-of-subcategories"""

        response = await self.make_request(
            method=HTTPMethod.GET, path="/api/v3/subcategories", continuation=continuation
        )
        return response

    async def make_request(
        self,
        *,
        method: HTTPMethod,
        path: str,
        body: dict[str, Any] | None = None,
        query: Mapping[str, Any] | None = None,
        continuation: str | None = None,
    ) -> aiohttp.ClientResponse:
        # Copy the params
        query = dict(query) if query else {}
        if continuation:
            query["continuation"] = continuation

        async def _req(session: aiohttp.ClientSession) -> aiohttp.ClientResponse:
            LOGGER.debug(
                "Eventbrite API Request",
                {
                    "method": method,
                    "path": path,
                    "body": body,
                    "query": query,
                    "api_key_idx": self._current_api_key_idx,
                },
            )

            response = await session.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params=query,
                json=body,
            )

            return response

        async with aiohttp.ClientSession(raise_for_status=False) as session:
            response = await _req(session)

            try_num = 0
            while response.status == 429 and try_num < len(self._api_keys):
                LOGGER.warning(
                    f"429 from Eventbrite; attempting key rotation ({self._current_api_key_idx + 1}/{len(self._api_keys)}"
                )
                # Rate limited. Switch to next API key and try again.
                try_num += 1
                self._increment_api_key_idx()
                response = await _req(session)

            response.raise_for_status()
            await response.read()  # Read the response body while the session is still open

        return response

    def _increment_api_key_idx(self) -> None:
        self._current_api_key_idx = (self._current_api_key_idx + 1) % len(self._api_keys)

    @property
    def api_key(self) -> str:
        try:
            return self._api_keys[self._current_api_key_idx]
        except KeyError:
            # This is a failsafe in case the key index math is wrong or something
            return self._api_keys[0]
