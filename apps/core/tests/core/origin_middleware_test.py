import time
from datetime import datetime
from http import HTTPStatus

import mockito

import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.enums as eave_enums
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.util as eave_util
import eave.stdlib.signing as eave_signing
import pytest
from sqlalchemy import select

from .base import BaseTestCase


class TestOriginMiddleware(BaseTestCase):
    async def test_origin_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            url="/status",
            headers={"eave-origin": None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_origin_header(self) -> None:
        response = await self.make_request(
            url="/access_request",
            payload={
                "visitor_id": self.anystring("visitor_id"),
                "email": f"{self.anystring('email')}@example.com",
                "opaque_input": self.anystring("opaque_input"),
            },
            headers={
                "eave-origin": None,
            }
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_invalid_origin(self) -> None:
        response = await self.make_request(
            url="/access_request",
            payload={
                "visitor_id": self.anystring("visitor_id"),
                "email": f"{self.anystring('email')}@example.com",
                "opaque_input": self.anystring("opaque_input"),
            },
            headers={
                "eave-origin": "invalid",
            }
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
