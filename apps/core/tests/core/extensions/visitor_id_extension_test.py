import re
from uuid import UUID

from google.cloud.kms import MacVerifyRequest, MacVerifyResponse

from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.core.orm.account import AccountOrm
from eave.stdlib.analytics import SEGMENT_ANONYMOUS_ID_COOKIE_NAME
from eave.stdlib.jwt import JWTPurpose, create_jws

from ..base import BaseTestCase


class TestVisitorIdExtension(BaseTestCase):
    async def test_visitor_id_extension_with_visitor_id_cookie(self) -> None:
        assert self.get_mock("segment.analytics.track").call_count == 0

        await self.make_graphql_request(
            "createAccount", # We're just using this endpoint because it uses visitor_id
            {
                "input": {
                    "email": self.anyemail(),
                    "plaintextPassword": self.anystr(),
                },
            },
            cookies={
                SEGMENT_ANONYMOUS_ID_COOKIE_NAME: self.anystr("visitor id")
            }
        )

        # Account doesn't have visitor_id so we're just checking something to make sure visitor_id was received.
        # It doesn't really matter what we're checking.
        assert self.get_mock("segment.analytics.track").call_count == 1
        assert self.get_mock("segment.analytics.track").call_args_list[0].kwargs["anonymous_id"] == self.getstr("visitor id")

    async def test_visitor_id_extension_without_visitor_id_cookie(self) -> None:
        assert self.get_mock("segment.analytics.track").call_count == 0

        await self.make_graphql_request(
            "createAccount", # We're just using this endpoint because it uses visitor_id
            {
                "input": {
                    "email": self.anyemail(),
                    "plaintextPassword": self.anystr(),
                },
            },
            cookies={}
        )

        # Account doesn't have visitor_id so we're just checking something to make sure visitor_id was received.
        # It doesn't really matter what we're checking.
        assert self.get_mock("segment.analytics.track").call_count == 1
        assert self.get_mock("segment.analytics.track").call_args_list[0].kwargs["anonymous_id"] is None
