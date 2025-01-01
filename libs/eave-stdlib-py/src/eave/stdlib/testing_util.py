# ruff: noqa: FBT001, FBT002, FBT003, S311

import base64
import hashlib
import json
import os
import random
import time
import unittest.mock
import uuid
import zoneinfo
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, tzinfo
from math import floor
from typing import Any, Literal, TypeVar, override
from zoneinfo import ZoneInfo

from google.cloud.kms import (
    CryptoKeyVersion,
    GetCryptoKeyVersionRequest,
    MacSignRequest,
    MacSignResponse,
    MacVerifyRequest,
    MacVerifyResponse,
)
from google.cloud.secretmanager import AccessSecretVersionRequest, AccessSecretVersionResponse, SecretPayload

import eave.stdlib.http_exceptions
from eave.stdlib.test_helpers.base_mixin import BaseMixin
from eave.stdlib.test_helpers.eventbrite_mocks_mixin import EventbriteMocksMixin
from eave.stdlib.test_helpers.google_cloud_mocks_mixin import GoogleCloudMocksMixin
from eave.stdlib.test_helpers.mocking_mixin import MockingMixin
from eave.stdlib.test_helpers.random_data_mixin import RandomDataMixin
from eave.stdlib.test_helpers.segment_mocks_mixin import SegmentMocksMixin
from eave.stdlib.test_helpers.sendgrid_mocks_mixin import SendgridMocksMixin
from eave.stdlib.test_helpers.slack_mocks_mixin import SlackMocksMixin
import eave.stdlib.util
from eave.stdlib.checksum import generate_checksum
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.models.logo import Logo
from eave.stdlib.eventbrite.models.shared import Address, CurrencyCost, MultipartText
from eave.stdlib.eventbrite.models.ticket_availability import TicketAvailability
from eave.stdlib.eventbrite.models.ticket_class import TicketClass
from eave.stdlib.eventbrite.models.venue import Venue
from eave.stdlib.time import ONE_YEAR_IN_SECONDS
from eave.stdlib.typing import NOT_SET, JsonObject


class UtilityBaseTestCase(GoogleCloudMocksMixin, SlackMocksMixin, EventbriteMocksMixin, SegmentMocksMixin, SendgridMocksMixin, MockingMixin, RandomDataMixin, BaseMixin):
    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        SHARED_CONFIG.reset_cached_properties()

    @staticmethod
    def unwrap[T](value: T | None) -> T:
        return eave.stdlib.util.unwrap(value)

    _increment = -1  # so that the first increment returns 0

    def increment(self) -> int:
        self._increment += 1
        return self._increment

    def b64encode(self, value: str, urlsafe: bool = False) -> str:
        b = value.encode()
        if urlsafe:
            return base64.urlsafe_b64encode(b).decode()
        else:
            return base64.b64decode(b).decode()

    def b64decode(self, value: str, urlsafe: bool = False) -> str:
        if urlsafe:
            return base64.urlsafe_b64decode(value).decode()
        else:
            return base64.b64decode(value).decode()

    @staticmethod
    def all_same(obj1: object, obj2: object, attrs: list[str] | None = None) -> bool:
        """
        Checks if all attributes `attrs` on objects `obj1` and `obj2` are the same value.
        """
        if not attrs:
            return obj1 == obj2
        else:
            # Using `all` seems like a better way to do this, but I deliberately don't because I want
            # to fully loop through `attrs` to catch an invalid/unset attribute. Globally renaming Python attributes in an IDE
            # doesn't update string references to those attributes, so this is a trade-off where it'll be caught during the tests
            # at runtime instead of during static analysis.
            # all(getattr(obj1, attr) == getattr(obj2, attr) for attr in attrs)

            passing = True
            for attr in attrs:
                a1 = getattr(obj1, attr)
                a2 = getattr(obj2, attr)
                if a1 != a2:
                    passing = False

            return passing

    @staticmethod
    def all_different(obj1: object, obj2: object, attrs: list[str] | None = None) -> bool:
        """
        Reciprical of `all_same`: Checks if all attributes `attrs` on objects `obj1` and `obj2` are a different value.
        This is not the same as `not all_same(...)`; that would pass if _any_ of the attributes were different,
        but we want to check if _all_ of the attributes are different, which is what this function does.
        """
        if not attrs:
            return obj1 != obj2
        else:
            passing = True
            for attr in attrs:
                a1 = getattr(obj1, attr)
                a2 = getattr(obj2, attr)
                if a1 == a2:
                    passing = False

            return passing
