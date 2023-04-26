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


class TestTeamLookupMiddleware(BaseTestCase):
    async def test_team_id_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            url="/status",
            headers={"eave-team-id": None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_team_id_header(self) -> None:
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
                "eave-team-id": None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_invalid_team_id(self) -> None:
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
                "eave-team-id": None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
