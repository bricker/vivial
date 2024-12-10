from google.cloud.kms import MacVerifyRequest, MacVerifyResponse
from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.core.orm.outing import OutingOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget
from eave.stdlib.jwt import JWTPurpose, create_jws

from ..base import BaseTestCase


class TestAuthenticationExtension(BaseTestCase):
    async def test_auth_extension_with_valid_access_token(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session=session)

        response = await self.make_graphql_request(
            "getReserverDetails",
            {},
            account_id=account.id,
        )

        assert ACCESS_TOKEN_COOKIE_NAME not in response.cookies
        assert REFRESH_TOKEN_COOKIE_NAME not in response.cookies

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["__typename"] == "AuthenticatedViewerQueries"

    async def test_auth_extension_with_expired_access_token(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session=session)

        expired_jws = create_jws(
            purpose=JWTPurpose.ACCESS,
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            subject=str(account.id),
            jwt_id=self.anystr(),
            max_age_minutes=-1, # this token is immediately expired
        )

        response = await self.make_graphql_request(
            "getReserverDetails",
            {},
            cookies={
                ACCESS_TOKEN_COOKIE_NAME: expired_jws
            },
        )

        assert ACCESS_TOKEN_COOKIE_NAME not in response.cookies
        assert REFRESH_TOKEN_COOKIE_NAME not in response.cookies

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["__typename"] == "UnauthenticatedViewer"
        assert result.data["viewer"]["authFailureReason"] == "ACCESS_TOKEN_EXPIRED"

    async def test_auth_extension_with_missing_access_token(self) -> None:
        response = await self.make_graphql_request(
            "getReserverDetails",
            {},
            account_id=None,
        )

        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) == ""
        assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) == ""

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["__typename"] == "UnauthenticatedViewer"
        assert result.data["viewer"]["authFailureReason"] == "ACCESS_TOKEN_INVALID"

    async def test_auth_extension_with_invalid_signature(self) -> None:
        def _verify_failure(request: MacVerifyRequest) -> MacVerifyResponse:
            return MacVerifyResponse(
                verified_data_crc32c=True,
                verified_mac_crc32c=True,
                name=request.name,
                success=False,
                verified_success_integrity=True,
            )

        self.get_mock("google.cloud.kms.KeyManagementServiceClient.mac_verify").side_effect = _verify_failure

        async with self.db_session.begin() as session:
            account = await self.make_account(session=session)

        response = await self.make_graphql_request(
            "getReserverDetails",
            {},
            account_id=account.id,
        )

        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) == ""
        assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) == ""

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["__typename"] == "UnauthenticatedViewer"
        assert result.data["viewer"]["authFailureReason"] == "ACCESS_TOKEN_INVALID"

    async def test_auth_extension_with_invalid_kms_response(self) -> None:
        def _verify_failure(request: MacVerifyRequest) -> MacVerifyResponse:
            return MacVerifyResponse(
                verified_data_crc32c=False,
                verified_mac_crc32c=False,
                name=request.name,
                success=True,
                verified_success_integrity=True,
            )

        self.get_mock("google.cloud.kms.KeyManagementServiceClient.mac_verify").side_effect = _verify_failure

        async with self.db_session.begin() as session:
            account = await self.make_account(session=session)

        response = await self.make_graphql_request(
            "getReserverDetails",
            {},
            account_id=account.id,
        )

        assert response.cookies.get(ACCESS_TOKEN_COOKIE_NAME) == ""
        assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) == ""

        result = self.parse_graphql_response(response)

        # When checksum validation fails, that's currently just an error from the server.
        assert not result.data
        assert result.errors and len(result.errors) == 1
