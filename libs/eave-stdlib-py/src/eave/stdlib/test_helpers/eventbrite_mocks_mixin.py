from collections.abc import AsyncIterator
from typing import Any, override
import unittest.mock

from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.models.logo import Logo
from eave.stdlib.eventbrite.models.shared import Address, CurrencyCost, MultipartText
from eave.stdlib.eventbrite.models.ticket_availability import TicketAvailability
from eave.stdlib.eventbrite.models.ticket_class import TicketClass
from eave.stdlib.eventbrite.models.venue import Venue
from eave.stdlib.test_helpers.mocking_mixin import MockingMixin
from eave.stdlib.test_helpers.random_data_mixin import RandomDataMixin


class EventbriteMocksMixin(MockingMixin, RandomDataMixin):
    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._add_eventbrite_client_mocks()

    mock_eventbrite_event: Event  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_eventbrite_ticket_class_batch: list[TicketClass]  # pyright: ignore [reportUninitializedInstanceVariable]

    def set_mock_eventbrite_ticket_class_batch(
        self, *, max_cost_cents: int | None = None, min_cost_cents: int | None = None
    ) -> None:
        if max_cost_cents is not None and min_cost_cents is None:
            if max_cost_cents == 0:
                min_cost_cents = 0
            else:
                min_cost_cents = 1

        self.mock_eventbrite_ticket_class_batch = [
            TicketClass(
                id=self.anydigits(),
                cost=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint(min=min_cost_cents, max=max_cost_cents),
                ),
                fee=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
                tax=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
            )
        ]

    def get_mock_eventbrite_ticket_class_batch_cost(self) -> int:
        # These checks are just for the typechecker
        cost = self.mock_eventbrite_ticket_class_batch[0].get("cost")
        fee = self.mock_eventbrite_ticket_class_batch[0].get("fee")
        tax = self.mock_eventbrite_ticket_class_batch[0].get("tax")
        assert cost and tax and fee

        return cost["value"] + fee["value"] + tax["value"]

    def _add_eventbrite_client_mocks(self) -> None:
        self.mock_eventbrite_event = Event(
            id=self.anydigits("eventbrite.Event.id"),
            name=MultipartText(
                text=self.anystr("eventbrite.Event.name.text"),
                html=self.anystr("eventbrite.Event.name.html"),
            ),
            status=EventStatus.LIVE,
            venue=Venue(
                address=Address(),
                latitude=str(self.anylatitude("eventbrite.Venue.latitude")),
                longitude=str(self.anylongitude("eventbrite.Venue.longitude")),
                name=self.anystr("eventbrite.Venue.name"),
            ),
            ticket_availability=TicketAvailability(
                has_available_tickets=True,
            ),
            logo=Logo(
                id=self.anydigits("eventbrite.Logo.id"),
                url=self.anyurl("eventbrite.Logo.url"),
            ),
            changed=self.anydatetime().isoformat(),
            created=self.anydatetime().isoformat(),
        )

        async def _mocked_eventbrite_get_event_by_id(**kwargs: Any) -> Event:
            return self.mock_eventbrite_event

        self.patch(
            name="eventbrite get_event_by_id",
            patch=unittest.mock.patch("eave.stdlib.eventbrite.client.EventbriteClient.get_event_by_id"),
            side_effect=_mocked_eventbrite_get_event_by_id,
        )

        self.mock_eventbrite_ticket_class_batch = [
            TicketClass(
                id=self.anydigits("eventbrite.TicketClass.0.id"),
                cost=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint("eventbrite.TicketClass.0.cost.value"),
                ),
                fee=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint("eventbrite.TicketClass.0.fee.value"),
                ),
                tax=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint("eventbrite.TicketClass.0.tax.value"),
                ),
            )
        ]

        async def _mocked_eventbrite_list_ticket_classes_for_sale_for_event(
            **kwargs: Any,
        ) -> AsyncIterator[list[TicketClass]]:
            yield self.mock_eventbrite_ticket_class_batch

        self.patch(
            name="EventbriteClient.list_ticket_classes_for_sale_for_event",
            patch=unittest.mock.patch(
                "eave.stdlib.eventbrite.client.EventbriteClient.list_ticket_classes_for_sale_for_event"
            ),
            side_effect=_mocked_eventbrite_list_ticket_classes_for_sale_for_event,
        )

        mock_eventbrite_description = MultipartText(
            text=self.anystr("eventbrite.EventDescription.text"),
            html=self.anystr("eventbrite.EventDescription.html"),
        )

        async def _mocked_eventbrite_get_event_description(**kwargs: Any) -> MultipartText:
            return mock_eventbrite_description

        self.patch(
            name="eventbrite get_event_description",
            patch=unittest.mock.patch("eave.stdlib.eventbrite.client.EventbriteClient.get_event_description"),
            side_effect=_mocked_eventbrite_get_event_description,
        )
