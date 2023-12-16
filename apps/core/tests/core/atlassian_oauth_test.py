import asyncio
import oauthlib.oauth2.rfc6749.tokens
import http
import json
import re
import urllib.parse
import uuid
from http import HTTPStatus
from eave.core.internal.oauth.state_cookies import EAVE_OAUTH_STATE_COOKIE_PREFIX
from eave.core.internal.orm.account import AccountOrm
from eave.core.public.requests.oauth.shared import DEFAULT_REDIRECT_LOCATION, DEFAULT_TEAM_NAME

import eave.stdlib.atlassian
from eave.stdlib.config import SHARED_CONFIG
import eave.core.internal
import eave.core.internal.oauth.atlassian
import eave.core.internal.oauth.google
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
import eave.core.internal.orm.team
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.auth_cookies import (
    EAVE_ACCOUNT_ID_COOKIE_NAME,
    EAVE_ACCESS_TOKEN_COOKIE_NAME,
)
from eave.stdlib.headers import LOCATION
from eave.stdlib.utm_cookies import EAVE_COOKIE_PREFIX_UTM

from .base import BaseTestCase


class TestAtlassianOAuth(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_token_update(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            sut = await AtlassianInstallationOrm.create(
                atlassian_cloud_id=self.anystr(),
                oauth_token_encoded=self.anyjson(),
                session=s,
                team_id=team.id,
            )

        token = oauthlib.oauth2.rfc6749.tokens.OAuth2Token(self.anydict("token"))
        sut.token_updater_factory()(token)
        await asyncio.gather(*sut._tasks)

        async with self.db_session.begin() as s:
            sut_after = await self.reload(s, sut)
            assert sut_after
            assert sut_after.oauth_token_decoded == token

    async def test_atlassian_authorize_endpoint(self) -> None:
        response = await self.make_request(
            eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_AUTHORIZE_PATH, method="GET", payload=None
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.cookies.get(f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}")
        assert response.headers[LOCATION]
        assert re.search(r"https://auth\.atlassian\.com/authorize", response.headers[LOCATION])
        redirect_uri = urllib.parse.quote(eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_URI, safe="")
        assert re.search(f"redirect_uri={redirect_uri}", response.headers[LOCATION])

    async def test_atlassian_authorize_with_utm_params(self) -> None:
        response = await self.make_request(
            path=eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_AUTHORIZE_PATH,
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

    async def test_atlassian_callback_new_account(self) -> None:
        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 0
            assert (await self.count(s, eave.core.internal.orm.AtlassianInstallationOrm)) == 0

        response = await self.make_request(
            path=eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}": self.anystr("state"),
                f"{EAVE_COOKIE_PREFIX_UTM}utm_campaign": self.anystr("utm_campaign"),
                f"{EAVE_COOKIE_PREFIX_UTM}gclid": self.anystr("gclid"),
            },
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert not response.cookies.get(
            f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}"
        )  # Test the cookie was deleted
        assert response.headers[LOCATION]
        assert response.headers[LOCATION] == DEFAULT_REDIRECT_LOCATION

        account_id = response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME)
        assert account_id
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self.anystr("atlassian.access_token")

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            assert (await self.count(s, eave.core.internal.orm.AtlassianInstallationOrm)) == 1

            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team

            atlassian_installation = await eave.core.internal.orm.AtlassianInstallationOrm.one_or_none(
                session=s, atlassian_cloud_id=self.anystr("atlassian_cloud_id")
            )
            assert atlassian_installation

            assert eave_account.opaque_utm_params is not None
            assert eave_account.opaque_utm_params.get("utm_campaign") == self.getstr("utm_campaign")
            assert eave_account.opaque_utm_params.get("gclid") == self.getstr("gclid")

            assert eave_account.access_token == self.getstr("atlassian.access_token")
            assert eave_account.refresh_token == self.getstr("atlassian.refresh_token")
            assert eave_account.auth_id == self.getstr("confluence.account_id")
            assert eave_account.auth_provider == AuthProvider.atlassian
            assert eave_team.name == self.getstr("atlassian.resource.name")
            assert eave_team.document_platform is None  # No connect installation has been linked yet
            assert atlassian_installation.oauth_token_encoded == json.dumps(self.testdata["fake_atlassian_token"])
            assert atlassian_installation.atlassian_cloud_id == self.getstr("atlassian_cloud_id")
            assert atlassian_installation.team_id == eave_team.id
            assert atlassian_installation.atlassian_site_name == self.getstr("atlassian.resource.name")

    async def test_atlassian_callback_new_account_without_team_name_from_atlassian(self) -> None:
        self.testdata["fake_atlassian_resources"][0].name = ""
        self.testdata["fake_atlassian_resources"][0].url = self.anystr("atlassian url")

        response = await self.make_request(
            path=eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}": self.anystr("state"),
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT
        account_id = response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME)

        async with self.db_session.begin() as s:
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team
            assert eave_team.name == f"{self.getstr('confluence.display_name')}'s Team"

            atlassian_installation = await eave.core.internal.orm.AtlassianInstallationOrm.one_or_none(
                session=s, atlassian_cloud_id=self.getstr("atlassian_cloud_id")
            )

            assert atlassian_installation
            assert atlassian_installation.atlassian_site_name == self.getstr("atlassian url")

    async def test_atlassian_callback_new_account_without_user_name_from_atlassian(self) -> None:
        self.testdata["fake_atlassian_resources"][0].name = ""
        self.testdata["fake_confluence_user"].display_name = None

        response = await self.make_request(
            path=eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}": self.anystr("state"),
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

    async def test_atlassian_callback_existing_account(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.atlassian,
                auth_id=self.anystr("confluence.account_id"),
                access_token=self.anystr("old_access_token"),
                refresh_token=self.anystr("old_refresh_token"),
            )

        response = await self.make_request(
            path=eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}": self.anystr("state"),
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await AccountOrm.one_or_exception(
                session=s, params=AccountOrm.QueryParams(id=eave_account_before.id)
            )

            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystr("atlassian.access_token")
            assert eave_account_after.refresh_token == self.anystr("atlassian.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_after.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_after.access_token

    async def test_atlassian_callback_logged_in_account(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.atlassian,
                auth_id=self.anystr("authed_user.id"),
                access_token=self.anystr("old_access_token"),
                refresh_token=self.anystr("old_refresh_token"),
            )

        response = await self.make_request(
            path=eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}": self.anystr("state"),
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(eave_account_before.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: eave_account_before.access_token,
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystr("atlassian.access_token")
            assert eave_account_after.refresh_token == self.anystr("atlassian.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_after.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_after.access_token

    async def test_atlassian_callback_logged_in_account_another_provider(self) -> None:
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
            path=eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}": self.anystr("state"),
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(eave_account_before.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: eave_account_before.access_token,
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were NOT updated
            assert eave_account_after.access_token == self.anystr("old_access_token")
            assert eave_account_after.refresh_token == self.anystr("old_refresh_token")

            # Test that the cookies were NOT updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_before.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_before.access_token

    async def test_atlassian_callback_invalid_state(self) -> None:
        response = await self.make_request(
            path=eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystr("code"),
                "state": self.anystr("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.atlassian}": self.anystr("invalid_state"),
            },
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 0
            assert (await self.count(s, eave.core.internal.orm.TeamOrm)) == 0

    async def test_atlassian_default_confluence_space(self) -> None:
        self.skipTest("TODO")

    async def test_urls(self):
        assert eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_AUTHORIZE_PATH == "/oauth/atlassian/authorize"
        assert eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_PATH == "/oauth/atlassian/callback"
        assert (
            eave.core.internal.oauth.atlassian.ATLASSIAN_OAUTH_CALLBACK_URI
            == f"{SHARED_CONFIG.eave_public_api_base}/oauth/atlassian/callback"
        )
