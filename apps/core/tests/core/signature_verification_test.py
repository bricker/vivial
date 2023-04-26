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


class TestSignatureVerification(BaseTestCase):
    async def test_signature_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            url="/status",
            headers={"eave-signature": None},
        )

        assert response.status_code == HTTPStatus.OK
        mockito.verify(eave_signing, times=0).verify_signature_or_exception(...)

    async def test_missing_signature_header(self) -> None:
        response = await self.make_request(
            url="/access_request",
            payload={
                "visitor_id": self.anystring("visitor_id"),
                "email": f"{self.anystring('email')}@example.com",
                "opaque_input": self.anystring("opaque_input"),
            },
            headers={
                "eave-signature": None,
            }
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        mockito.verify(eave_signing, times=0).verify_signature_or_exception(...)

    async def test_mismatched_signature(self) -> None:
        response = await self.make_request(
            url="/access_request",
            payload={
                "visitor_id": self.anystring("visitor_id"),
                "email": f"{self.anystring('email')}@example.com",
                "opaque_input": self.anystring("opaque_input"),
            },
            headers={
                "eave-signature": "sdfdsfs",
            }
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        mockito.verify(eave_signing, times=1).verify_signature_or_exception(...)

    async def test_empty_body(self) -> None:
        response = await self.make_request(
            url="/access_request",
            payload=None,
            headers={}
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        mockito.verify(eave_signing, times=0).verify_signature_or_exception(...)

    async def test_signature_with_team_id(self) -> None:
        team = await self.make_team()
        response = await self.make_request(
            url="/subscriptions/create",
            payload={
                "subscription": {
                    "source": {
                        "platform": "slack",
                        "event": "slack_message",
                        "id": self.anystring("source_id"),
                    },
                },
            },
            headers={
                "eave-team-id": str(team.id),
            }
        )

        assert response.status_code == HTTPStatus.CREATED
        mockito.verify(eave_signing, times=1).verify_signature_or_exception(...)
