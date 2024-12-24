import os
import random
import unittest.mock
from datetime import timedelta
from http import HTTPStatus
from typing import Any, Protocol, TypeVar, override
from uuid import UUID

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql.functions as safunc
import stripe
from google.maps.places import PhotoMedia
from google.maps.places_v1.types import Place
from google.maps.routing import ComputeRoutesResponse, Route
from google.protobuf.duration_pb2 import Duration
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy import literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import ExecutionResult

import eave.core.app
import eave.core.database
import eave.core.orm
import eave.stdlib.testing_util
import eave.stdlib.typing
from eave.core._database_setup import get_base_metadata, init_database
from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME
from eave.core.config import CORE_API_APP_CONFIG, JWT_AUDIENCE, JWT_ISSUER
from eave.core.lib.address import Address
from eave.core.lib.google_places import GeocodeGeometry, GeocodeLocation, GeocodeResult
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
from eave.dev_tooling.constants import EAVE_HOME
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.jwt import JWTPurpose, create_jws
from eave.stdlib.time import ONE_DAY_IN_SECONDS, ONE_YEAR_IN_MINUTES


class AnyStandardOrm(Protocol):
    id: sqlalchemy.orm.Mapped[UUID]


T = TypeVar("T")
J = TypeVar("J", bound=AnyStandardOrm)

_db_setup: bool = False


class MockPlacesResponse:
    places: list[Place]

    def __init__(self, places: list[Place]) -> None:
        self.places = places


# eave.core.database.async_engine.echo = True


class BaseTestCase(eave.stdlib.testing_util.UtilityBaseTestCase):
    _gql_cache: dict[str, str]  # pyright: ignore [reportUninitializedInstanceVariable]

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    @override
    async def asyncSetUp(self) -> None:
        global _db_setup

        # Attempt to prevent running destructive database operations against non-test database
        assert os.environ["EAVE_ENV"] == "test", "Tests must be run with EAVE_ENV=test"
        assert (
            eave.core.database.async_engine.url.database == "eave-test"
        ), 'Tests perform destructive database operations, and can only be run against the test database (hardcoded to be "eave-test")'

        if not _db_setup:
            print("Running one-time DB setup...")
            await init_database()
            _db_setup = True

        CORE_API_APP_CONFIG.reset_cached_properties()

        await super().asyncSetUp()
        self._add_google_places_client_mocks()
        self._add_stripe_client_mocks()
        self._add_google_routes_client_mocks()
        self._add_google_maps_client_mocks()

        engine = eave.core.database.async_engine.execution_options(isolation_level="READ COMMITTED")
        self.db_session = eave.core.database.async_sessionmaker(engine, expire_on_commit=False)  # pyright: ignore [reportUninitializedInstanceVariable]

        transport = ASGITransport(
            app=eave.core.app.app,
            raise_app_exceptions=True,
        )
        self.httpclient = AsyncClient(  # pyright: ignore [reportUninitializedInstanceVariable]
            base_url=SHARED_CONFIG.eave_api_base_url_public,
            transport=transport,
        )

        self._gql_cache = {}

    @override
    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    @override
    async def cleanup(self) -> None:
        await super().cleanup()

        tnames = ",".join([t.name for t in get_base_metadata().sorted_tables])
        conn = await self.db_session().connection()
        await conn.execute(text(f"TRUNCATE {tnames} CASCADE").execution_options(autocommit=True))
        await conn.commit()
        await conn.close()
        await eave.core.database.async_engine.dispose()
        await self.httpclient.aclose()

    def load_graphql_query(self, name: str) -> str:
        if name not in self._gql_cache:
            with open(f"{EAVE_HOME}/apps/core/tests/core/resolvers/graphql/{name}.graphql") as f:
                self._gql_cache[name] = f.read()

        return self._gql_cache[name]

    async def reload(self, session: AsyncSession, /, obj: J) -> J | None:
        stmt = select(obj.__class__).where(literal_column("id") == obj.id)
        result: J | None = await session.scalar(stmt)
        return result

    async def delete(self, session: AsyncSession, /, obj: AnyStandardOrm) -> None:
        await session.delete(obj)

    async def count(self, session: AsyncSession, /, cls: type[AnyStandardOrm]) -> int:
        query = select(safunc.count(cls.id))
        count: int | None = await session.scalar(query)

        if count is None:
            count = 0
        return count

    def anyaddress(self, name: str | None = None) -> Address:
        name = self._make_testdata_name(name)

        data = Address(
            address1=self.anystr(),
            address2=self.anystr(),
            city=self.anystr(),
            country=self.anystr(),
            state=self.anyusstate(),
            zip_code=self.anydigits(length=5),
        )

        self.testdata[name] = data
        return self.getaddress(name)

    def getaddress(self, name: str) -> Address:
        return self.testdata[name]

    def anycoordinates(self, name: str | None = None) -> GeoPoint:
        name = self._make_testdata_name(name)

        data = GeoPoint(
            lat=self.anylatitude(),
            lon=self.anylongitude(),
        )

        self.testdata[name] = data
        return self.getcoordinates(name)

    def getcoordinates(self, name: str) -> GeoPoint:
        return self.testdata[name]

    def parse_graphql_response(self, response: Response) -> ExecutionResult:
        j = response.json()

        result = ExecutionResult(
            data=j.get("data"),
            errors=j.get("errors"),
        )

        return result

    async def make_graphql_request(
        self,
        query_name: str,
        variables: dict[str, Any],
        *,
        account_id: UUID | None = None,
        cookies: dict[str, str] | None = None,
    ) -> Response:
        if cookies is None:
            cookies = {}

        if account_id and ACCESS_TOKEN_COOKIE_NAME not in cookies:
            jws = create_jws(
                purpose=JWTPurpose.ACCESS,
                issuer=JWT_ISSUER,
                audience=JWT_AUDIENCE,
                subject=str(account_id),
                jwt_id=self.anystr(),
                max_age_minutes=ONE_YEAR_IN_MINUTES,
            )

            cookies[ACCESS_TOKEN_COOKIE_NAME] = jws

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": self.load_graphql_query(query_name),
                "variables": variables,
            },
            cookies=cookies,
        )

        assert response.status_code == HTTPStatus.OK
        return response

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

    mock_stripe_payment_intent: stripe.PaymentIntent  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_stripe_customer: stripe.Customer  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_stripe_customer_session: stripe.CustomerSession  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_stripe_customer_payment_methods: list[stripe.PaymentMethod]  # pyright: ignore [reportUninitializedInstanceVariable]

    def _add_stripe_client_mocks(self) -> None:
        mock_stripe_payment_intent = stripe.PaymentIntent(
            id=self.anystr("stripe.PaymentIntent.id"),
        )
        mock_stripe_payment_intent.client_secret = self.anystr("stripe.PaymentIntent.client_secret")
        mock_stripe_payment_intent.status = "requires_capture"
        self.mock_stripe_payment_intent = mock_stripe_payment_intent

        async def _mock_payment_intent_create_async(**kwargs: Any) -> stripe.PaymentIntent:
            return self.mock_stripe_payment_intent

        self.patch(
            name="stripe.PaymentIntent.create_async",
            patch=unittest.mock.patch("stripe.PaymentIntent.create_async"),
            side_effect=_mock_payment_intent_create_async,
        )

        async def _mock_payment_intent_retrieve_async(**kwargs: Any) -> stripe.PaymentIntent:
            return self.mock_stripe_payment_intent

        self.patch(
            name="stripe.PaymentIntent.retrieve_async",
            patch=unittest.mock.patch("stripe.PaymentIntent.retrieve_async"),
            side_effect=_mock_payment_intent_retrieve_async,
        )

        self.mock_stripe_customer = stripe.Customer(
            id=self.anystr("stripe.Customer.id"),
        )

        async def _mock_customer_create_async(**kwargs: Any) -> stripe.Customer:
            return self.mock_stripe_customer

        self.patch(
            name="stripe.Customer.create_async",
            patch=unittest.mock.patch("stripe.Customer.create_async"),
            side_effect=_mock_customer_create_async,
        )

        self.mock_stripe_customer_payment_methods = [
            stripe.PaymentMethod(
                id=self.anystr(),
            ),
        ]

        setattr(
            self.mock_stripe_customer_payment_methods[0],
            "card",
            stripe.Card(
                brand="visa",
                last4=self.anydigits(length=4),
                exp_month=self.anyint(min=1, max=12),
                exp_year=self.anyint(min=2020, max=2100),
            ),
        )

        async def _mock_customer_list_payment_methods(*args: Any, **kwargs: Any) -> list[stripe.PaymentMethod]:
            return self.mock_stripe_customer_payment_methods

        self.patch(
            name="stripe.Customer.list_payment_methods_async",
            patch=unittest.mock.patch("stripe.Customer.list_payment_methods_async"),
            side_effect=_mock_customer_list_payment_methods,
        )

        self.mock_stripe_customer_session = stripe.CustomerSession()
        self.mock_stripe_customer_session.client_secret = self.anystr("stripe.CustomerSession.client_secret")

        async def _mock_customer_session_create_async(**kwargs: Any) -> stripe.CustomerSession:
            return self.mock_stripe_customer_session

        self.patch(
            name="stripe.CustomerSession.create_async",
            patch=unittest.mock.patch("stripe.CustomerSession.create_async"),
            side_effect=_mock_customer_session_create_async,
        )

    mock_google_place: Place  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_google_places_photo_media: PhotoMedia  # pyright: ignore [reportUninitializedInstanceVariable]

    def _add_google_places_client_mocks(self) -> None:
        self.mock_google_place = Place(
            id=self.anystr("Place.id"),
        )

        async def _mock_google_places_search_nearby(*args, **kwargs) -> MockPlacesResponse:
            return MockPlacesResponse(places=[self.mock_google_place])

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

    mock_compute_routes_response: ComputeRoutesResponse  # pyright: ignore [reportUninitializedInstanceVariable]

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

    mock_maps_geocoding_response: list[GeocodeResult]  # pyright: ignore [reportUninitializedInstanceVariable]

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

        def _mock_google_maps_geocode(*args, **kwargs) -> list[GeocodeResult]:
            return self.mock_maps_geocoding_response

        self.patch(
            name="google maps geocode",
            patch=unittest.mock.patch("googlemaps.geocoding.geocode"),
            side_effect=_mock_google_maps_geocode,
        )

    def random_search_areas(self, k: int = 3) -> list[SearchRegionOrm]:
        return random.choices(SearchRegionOrm.all(), k=k)

    def random_restaurant_categories(self, k: int = 3) -> list[RestaurantCategoryOrm]:
        return random.choices(RestaurantCategoryOrm.all(), k=k)

    def random_activity_categories(self, k: int = 3) -> list[ActivityCategoryOrm]:
        return random.choices(ActivityCategoryOrm.all(), k=k)

    def random_outing_budget(self) -> OutingBudget:
        return random.choice(list(OutingBudget))
