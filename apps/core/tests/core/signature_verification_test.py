import time
from datetime import datetime
from http import HTTPStatus

import mockito

import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.enums as eave_models
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.util as eave_util
import eave.stdlib.signing as eave_signing
import pytest
from sqlalchemy import select

from .base import BaseTestCase


class TestSignatureVerification(BaseTestCase):
    async def test_bypass(self) -> None:
        pass

    async def test_missing_signature_header(self) -> None:
        response = await self.make_request(
            url="/auth/token/request",
            payload={
                "exchange_offer": {
                    "auth_provider": eave_models.AuthProvider.slack,
                    "auth_id": self.anystring("auth_id_invalid"),
                    "oauth_token": self.anystring("oauth_token_invalid"),
                }
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    async def test_empty_body(self) -> None:
        pass

    async def test_signature_with_team_id(self) -> None:
        pass

    async def test_signature_without_team_id(self) -> None:
        pass
