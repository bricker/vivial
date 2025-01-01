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
from google.maps.places import PhotoMedia
from google.maps.places_v1.types import Place
from google.maps.routing import ComputeRoutesResponse, Route
from google.protobuf.duration_pb2 import Duration
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy import literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from strawberry.types import ExecutionResult

import eave.core.app
import eave.core.database
import eave.core.orm
from eave.stdlib.testing_util import UtilityBaseTestCase
import eave.stdlib.typing
from eave.core._database_setup import get_base_metadata, init_database
from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME
from eave.core.config import CORE_API_APP_CONFIG, JWT_AUDIENCE, JWT_ISSUER
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
from eave.dev_tooling.constants import EAVE_HOME
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.jwt import JWTPurpose, create_jws
from eave.stdlib.time import ONE_DAY_IN_SECONDS, ONE_YEAR_IN_MINUTES
from ._helpers.http_client_mixin import HTTPClientMixin
from ._helpers.google_places_mocks_mixin import GooglePlacesMocksMixin
from ._helpers.graphql_mixin import GraphQLMixin
from ._helpers.orm_helpers_mixin import OrmHelpersMixin
from ._helpers.random_instance_mixin import RandomInstanceMixin
from ._helpers.stripe_mocks_mixin import StripeMocksMixin


_db_setup: bool = False

# eave.core.database.async_engine.echo = True


class BaseTestCase(RandomInstanceMixin, GraphQLMixin, OrmHelpersMixin, GooglePlacesMocksMixin, StripeMocksMixin, UtilityBaseTestCase, HTTPClientMixin):
    db_session: async_sessionmaker[AsyncSession]  # pyright: ignore [reportUninitializedInstanceVariable]

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

        engine = eave.core.database.async_engine.execution_options(isolation_level="READ COMMITTED")
        self.db_session = eave.core.database.async_sessionmaker(engine, expire_on_commit=False)

    @override
    async def cleanup(self) -> None:
        await super().cleanup()

        tnames = ",".join([t.name for t in get_base_metadata().sorted_tables])
        conn = await self.db_session().connection()
        await conn.execute(text(f"TRUNCATE {tnames} CASCADE").execution_options(autocommit=True))
        await conn.commit()
        await conn.close()
        await eave.core.database.async_engine.dispose()
