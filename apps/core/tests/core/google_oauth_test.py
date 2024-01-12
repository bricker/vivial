import http
import re
import unittest.mock
import urllib.parse
import uuid
from http import HTTPStatus
from typing import Any
import aiohttp

import google.oauth2.credentials
import google.oauth2.id_token
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.team import TeamOrm

from eave.stdlib.config import SHARED_CONFIG
import eave.core.internal
import eave.core.internal.oauth.google
import eave.core.internal.oauth.slack
from eave.core.internal.oauth.state_cookies import EAVE_OAUTH_STATE_COOKIE_PREFIX
from eave.core.public.requests.oauth.shared import DEFAULT_REDIRECT_LOCATION, DEFAULT_TEAM_NAME
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.auth_cookies import (
    EAVE_ACCOUNT_ID_COOKIE_NAME,
    EAVE_ACCESS_TOKEN_COOKIE_NAME,
)
from eave.stdlib.utm_cookies import EAVE_COOKIE_PREFIX_UTM
from .base import BaseTestCase


class TestGoogleOAuthHandler(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        def id_token() -> dict[str, str]:
            return {
                "sub": self.anystr("google.sub"),
                "given_name": self.anystr("google.given_name"),
                "email": self.anystr("google.email"),
            }

        def _verify_oauth2_token(*args: Any, **kwargs: Any) -> dict[str, str]:
            return id_token()

        self.patch(unittest.mock.patch("google.oauth2.id_token.verify_oauth2_token", side_effect=_verify_oauth2_token))

        def _credentials_from_session(*args: Any, **kwargs: Any) -> google.oauth2.credentials.Credentials:
            return google.oauth2.credentials.Credentials(
                token=self.anystr("google.token"),
                refresh_token=self.anystr("google.refresh_token"),
                id_token=id_token(),
            )

        self.patch(
            unittest.mock.patch(
                "google_auth_oauthlib.helpers.credentials_from_session", side_effect=_credentials_from_session
            )
        )
        self.patch(unittest.mock.patch("google_auth_oauthlib.flow.Flow.fetch_token"))

    async def test_google_authorize(self) -> None:
        response = await self.make_request(
            path=eave.core.internal.oauth.google.GOOGLE_OAUTH_AUTHORIZE_PATH,
            sign=False,
            method="GET",
            payload=None,
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.cookies.get(f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.google}")
        assert response.headers[aiohttp.hdrs.LOCATION]
        assert re.search(r"^https://accounts\.google\.com/o/oauth2/auth", response.headers[aiohttp.hdrs.LOCATION])
        redirect_uri = urllib.parse.quote(eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_URI, safe="")
        assert re.search(redirect_uri, response.headers[aiohttp.hdrs.LOCATION])

    async def test_google_authorize_with_utm_params(self) -> None:
        response = await self.make_request(
            path=eave.core.internal.oauth.google.GOOGLE_OAUTH_AUTHORIZE_PATH,
            sign=False,
            method="GET",
            payload={
                "utm_campaign": self.anystr("utm_campaign"),
                "gclid": self.anystr("gclid"),
                "ignored_param": self.anystr(),
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT
        assert response.cookies.get(f"{EAVE_COOKIE_PREFIX_UTM}utm_campaign") == self.getstr("utm_campaign")
        assert response.cookies.get(f"{EAVE_COOKIE_PREFIX_UTM}gclid") == self.getstr("gclid")
        assert response.cookies.get(f"{EAVE_COOKIE_PREFIX_UTM}ignored_param") is None

    async def test_google_callback_new_account(self) -> None:
        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 0

        response = await self.make_request(
            path=eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.google}": self.anystr("state"),
                f"{EAVE_COOKIE_PREFIX_UTM}utm_campaign": self.anystr("utm_campaign"),
                f"{EAVE_COOKIE_PREFIX_UTM}gclid": self.anystr("gclid"),
            },
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert not response.cookies.get(
            f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.google}"
        )  # Test the cookie was deleted
        assert response.headers[aiohttp.hdrs.LOCATION]
        assert response.headers[aiohttp.hdrs.LOCATION] == DEFAULT_REDIRECT_LOCATION

        account_id = response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME)
        assert account_id
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 1

            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team

            assert eave_account.opaque_utm_params is not None
            assert eave_account.opaque_utm_params.get("utm_campaign") == self.getstr("utm_campaign")
            assert eave_account.opaque_utm_params.get("gclid") == self.getstr("gclid")

            assert eave_account.access_token == self.anystr("google.token")
            assert eave_account.refresh_token == self.anystr("google.refresh_token")
            assert eave_account.auth_id == self.anystr("google.sub")
            assert eave_account.auth_provider == AuthProvider.google
            assert eave_team.name == f"{self.anystr('google.given_name')}'s Team"

    async def test_google_callback_new_account_without_name_from_google(self) -> None:
        self.testdata["google.given_name"] = None

        response = await self.make_request(
            path=eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.google}": self.anystr("state"),
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT
        account_id = response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME)
        async with self.db_session.begin() as s:
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team
            assert eave_team.name == DEFAULT_TEAM_NAME

    async def test_google_callback_existing_account(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.google,
                auth_id=self.anystr("google.sub"),
                access_token=self.anystr("old_access_token"),
                refresh_token=self.anystr("old_refresh_token"),
            )

        response = await self.make_request(
            path=eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.google}": self.anystr("state"),
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystr("google.token")
            assert eave_account_after.refresh_token == self.anystr("google.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_after.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_after.access_token

    async def test_google_callback_logged_in_account(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.google,
                auth_id=self.anystr("google.sub"),
                access_token=self.anystr("old_access_token"),
                refresh_token=self.anystr("old_refresh_token"),
            )

        response = await self.make_request(
            path=eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.google}": self.anystr("state"),
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(eave_account_before.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: eave_account_before.access_token,
            },
        )
        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystr("google.token")
            assert eave_account_after.refresh_token == self.anystr("google.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_after.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_after.access_token

    async def test_google_callback_logged_in_account_another_provider(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.slack,
                auth_id=self.anystr("slack.user_id"),
                access_token=self.anystr("old_access_token"),
                refresh_token=self.anystr("old_refresh_token"),
            )

        response = await self.make_request(
            path=eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.google}": self.anystr("state"),
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(eave_account_before.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: eave_account_before.access_token,
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were NOT updated
            assert eave_account_after.access_token == self.anystr("old_access_token")
            assert eave_account_after.refresh_token == self.anystr("old_refresh_token")

            # Test that the cookies were NOT updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_before.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_before.access_token

    async def test_google_callback_invalid_state(self) -> None:
        response = await self.make_request(
            path=eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.google}": self.anystr("invalid_state"),
            },
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 0
            assert (await self.count(s, TeamOrm)) == 0

    async def test_urls(self):
        assert eave.core.internal.oauth.google.GOOGLE_OAUTH_AUTHORIZE_PATH == "/oauth/google/authorize"
        assert eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_PATH == "/oauth/google/callback"
        assert (
            eave.core.internal.oauth.google.GOOGLE_OAUTH_CALLBACK_URI
            == f"{SHARED_CONFIG.eave_public_api_base}/oauth/google/callback"
        )
