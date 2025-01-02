from eave.core.shared.enums import ActivitySource, BookingState, OutingBudget, RestaurantSource
from ..base import BaseTestCase


class TestSharedEnums(BaseTestCase):
    async def test_booking_state_values(self) -> None:
        assert BookingState.INITIATED.value == "INITIATED"
        assert BookingState.CONFIRMED.value == "CONFIRMED"
        assert BookingState.BOOKED.value == "BOOKED"
        assert BookingState.CANCELED.value == "CANCELED"

    async def test_booking_state_visibility(self) -> None:
        assert BookingState.INITIATED.is_visible is False
        assert BookingState.CONFIRMED.is_visible is True
        assert BookingState.BOOKED.is_visible is True
        assert BookingState.CANCELED.is_visible is False

    async def test_outing_budget_values(self) -> None:
        assert OutingBudget.FREE.value == 1
        assert OutingBudget.INEXPENSIVE.value == 2
        assert OutingBudget.MODERATE.value == 3
        assert OutingBudget.EXPENSIVE.value == 4
        assert OutingBudget.VERY_EXPENSIVE.value == 5

    async def test_activity_source_values(self) -> None:
        assert ActivitySource.INTERNAL.value == "INTERNAL"
        assert ActivitySource.EVENTBRITE.value == "EVENTBRITE"
        assert ActivitySource.GOOGLE_PLACES.value == "GOOGLE_PLACES"

    async def test_restaurant_source_values(self) -> None:
        assert RestaurantSource.GOOGLE_PLACES.value == "GOOGLE_PLACES"
