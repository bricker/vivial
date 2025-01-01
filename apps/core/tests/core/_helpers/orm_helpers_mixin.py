from datetime import timedelta
import random
from typing import Protocol
from uuid import UUID
from sqlalchemy import literal_column, select
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.sql.functions as safunc

from eave.core.lib.address import Address
from eave.core.orm.account import AccountOrm
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource
from eave.core.shared.geo import GeoPoint
from eave.stdlib.test_helpers.eventbrite_mocks_mixin import EventbriteMocksMixin
from eave.stdlib.test_helpers.random_data_mixin import RandomDataMixin
from eave.stdlib.time import ONE_DAY_IN_SECONDS
from .google_places_mocks_mixin import GooglePlacesMocksMixin
from .stripe_mocks_mixin import StripeMocksMixin

class AnyStandardOrm(Protocol):
    id: sqlalchemy.orm.Mapped[UUID]

class OrmHelpersMixin(GooglePlacesMocksMixin, StripeMocksMixin, EventbriteMocksMixin, RandomDataMixin):
    def make_account(
        self,
        session: AsyncSession,
    ) -> AccountOrm:
        account = AccountOrm(
            session,
            email=self.anyemail(),
            plaintext_password=self.anystr(),
        )

        return account

    def make_survey(self, session: AsyncSession, account: AccountOrm | None) -> SurveyOrm:
        survey = SurveyOrm(
            session,
            account=account,
            budget=self.random_outing_budget(),
            headcount=self.anyint(min=1, max=2),
            search_area_ids=[s.id for s in self.random_search_areas(k=3)],
            start_time_utc=self.anydatetime(
                offset=self.anyint(min=ONE_DAY_IN_SECONDS * 2, max=ONE_DAY_IN_SECONDS * 14),
            ),
            timezone=self.anytimezone(),
            visitor_id=self.anystr(),
        )
        return survey

    def make_outing(self, session: AsyncSession, account: AccountOrm | None, survey: SurveyOrm) -> OutingOrm:
        outing = OutingOrm(
            session,
            visitor_id=survey.visitor_id,
            account=account,
            survey=survey,
        )

        outing.activities.append(
            OutingActivityOrm(
                session,
                outing=outing,
                headcount=survey.headcount,
                source=ActivitySource.EVENTBRITE,
                source_id=self.getdigits("eventbrite.Event.id"),
                start_time_utc=survey.start_time_utc + timedelta(hours=2),
                timezone=survey.timezone,
            )
        )

        outing.reservations.append(
            OutingReservationOrm(
                session,
                outing=outing,
                headcount=survey.headcount,
                source=RestaurantSource.GOOGLE_PLACES,
                source_id=self.getstr("Place.id"),
                start_time_utc=survey.start_time_utc,
                timezone=survey.timezone,
            )
        )

        return outing

    def make_reserver_details(self, session: AsyncSession, account: AccountOrm) -> ReserverDetailsOrm:
        reserver_details = ReserverDetailsOrm(
            session,
            account=account,
            first_name=self.anystr(),
            last_name=self.anystr(),
            phone_number=self.anyphonenumber(),
        )
        return reserver_details

    def make_stripe_payment_intent_reference(
        self, session: AsyncSession, account: AccountOrm
    ) -> StripePaymentIntentReferenceOrm:
        stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
            session, account=account, stripe_payment_intent_id=self.mock_stripe_payment_intent.id
        )
        return stripe_payment_intent_reference

    def make_booking(
        self,
        session: AsyncSession,
        account: AccountOrm,
        outing: OutingOrm,
        stripe_payment_intent_reference: StripePaymentIntentReferenceOrm | None = None,
        reserver_details: ReserverDetailsOrm | None = None,
    ) -> BookingOrm:
        booking = BookingOrm(
            session,
            outing=outing,
            accounts=[account],
            reserver_details=reserver_details,
            stripe_payment_intent_reference=stripe_payment_intent_reference,
        )

        booking_activity_template = BookingActivityTemplateOrm(
            session,
            booking=booking,
            name=self.anystr(),
            start_time_utc=outing.activities[0].start_time_utc,
            timezone=self.anytimezone(),
            photo_uri=self.anyurl(),
            headcount=outing.survey.headcount if outing.survey else self.anyint(min=1, max=2),
            coordinates=GeoPoint(
                lat=self.anylatitude(),
                lon=self.anylongitude(),
            ),
            external_booking_link=self.anyurl(),
            source=ActivitySource.EVENTBRITE,
            source_id=self.mock_eventbrite_event.get("id", "MISSING"),
            address=Address(
                address1=self.anystr(),
                address2=self.anystr(),
                city=self.anystr(),
                country="US",
                state=self.anyusstate(),
                zip_code=self.anydigits(),
            ),
        )
        booking.activities.append(booking_activity_template)

        booking_reservation_template = BookingReservationTemplateOrm(
            session,
            booking=booking,
            name=self.anystr(),
            photo_uri=self.anyurl(),
            start_time_utc=outing.reservations[0].start_time_utc,
            timezone=self.anytimezone(),
            headcount=outing.survey.headcount if outing.survey else self.anyint(min=1, max=2),
            coordinates=GeoPoint(
                lat=self.anylatitude(),
                lon=self.anylongitude(),
            ),
            external_booking_link=self.anyurl(),
            source=RestaurantSource.GOOGLE_PLACES,
            source_id=self.mock_google_place.id,
            address=Address(
                address1=self.anystr(),
                address2=self.anystr(),
                city=self.anystr(),
                country="US",
                state=self.anyusstate(),
                zip_code=self.anydigits(),
            ),
        )
        booking.reservations.append(booking_reservation_template)

        return booking

    def random_search_areas(self, k: int = 3) -> list[SearchRegionOrm]:
        return random.choices(SearchRegionOrm.all(), k=k)

    def random_restaurant_categories(self, k: int = 3) -> list[RestaurantCategoryOrm]:
        return random.choices(RestaurantCategoryOrm.all(), k=k)

    def random_activity_categories(self, k: int = 3) -> list[ActivityCategoryOrm]:
        return random.choices(ActivityCategoryOrm.all(), k=k)

    def random_outing_budget(self) -> OutingBudget:
        return random.choice(list(OutingBudget))

    async def reload[T: AnyStandardOrm](self, session: AsyncSession, /, obj: T) -> T | None:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        result: T | None = await session.scalar(stmt)
        return result

    async def delete(self, session: AsyncSession, /, obj: AnyStandardOrm) -> None:
        await session.delete(obj)

    async def count(self, session: AsyncSession, /, cls: type[AnyStandardOrm]) -> int:
        query = select(safunc.count(cls.id))
        count: int | None = await session.scalar(query)

        if count is None:
            count = 0
        return count
