import datetime
import http
import re
import typing
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import aiohttp
from eave.stdlib.metabase_api import MetabaseApiClient
import oauthlib.common
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal.bigquery.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.config import CORE_API_APP_CONFIG
import eave.core.internal.oauth.state_cookies
import eave.pubsub_schemas
import eave.stdlib.analytics
import eave.stdlib.config
import eave.stdlib.cookies
import eave.stdlib.exceptions
import eave.stdlib.slack
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib import auth_cookies, utm_cookies
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.logging import eaveLogger
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import ensure_uuid

from . import EAVE_ERROR_CODE_QP, EaveOnboardingErrorCode

DEFAULT_TEAM_NAME = "Your Team"
DEFAULT_REDIRECT_LOCATION = SHARED_CONFIG.eave_public_dashboard_base
SIGNUP_REDIRECT_LOCATION = f"{SHARED_CONFIG.eave_public_dashboard_base}/signup"


def verify_oauth_state_or_exception(
    state: str | None,
    auth_provider: AuthProvider,
    request: Request,
    response: Response,
) -> typing.Literal[True]:
    # verify request not tampered
    cookie_state = eave.core.internal.oauth.state_cookies.get_state_cookie(request=request, provider=auth_provider)
    eave.core.internal.oauth.state_cookies.delete_state_cookie(response=response, provider=auth_provider)

    if not state or not cookie_state or state != cookie_state:
        raise eave.stdlib.exceptions.InvalidStateError()

    return True


def set_redirect(response: Response, location: str) -> Response:
    response.headers[aiohttp.hdrs.LOCATION] = location
    response.status_code = http.HTTPStatus.TEMPORARY_REDIRECT
    return response


def set_error_code(response: Response, error_code: EaveOnboardingErrorCode) -> Response:
    location_header = response.headers[aiohttp.hdrs.LOCATION]
    location = urlparse(location_header)
    qs = parse_qs(location.query)
    qs.update({EAVE_ERROR_CODE_QP: [error_code.value]})
    qs_updated = urlencode(qs, doseq=True)
    location = location._replace(query=qs_updated)
    return set_redirect(response=response, location=urlunparse(location))


def is_error_response(response: Response) -> bool:
    location_header = response.headers[aiohttp.hdrs.LOCATION]
    location = urlparse(location_header)
    qs = parse_qs(location.query)
    return qs.get(EAVE_ERROR_CODE_QP) is not None


def cancel_flow(response: Response) -> Response:
    return set_redirect(response=response, location=SHARED_CONFIG.eave_public_dashboard_base)


async def get_logged_in_eave_account(
    request: Request,
    auth_provider: AuthProvider,
    access_token: str,
    refresh_token: str | None,
) -> AccountOrm | None:
    """
    Check if the user is logged in, and if so, get the account associated with the provided access token and account ID.
    """
    auth_cookies_ = auth_cookies.get_auth_cookies(cookies=request.cookies)

    if auth_cookies_.access_token and auth_cookies_.account_id:
        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_account = await AccountOrm.one_or_none(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=ensure_uuid(auth_cookies_.account_id),
                    access_token=auth_cookies_.access_token,
                ),
            )

            if not eave_account:
                # The access token or account ID are invalid. Treat this user as signed out.
                return None

            if eave_account.auth_provider == auth_provider:
                eave_account.set_tokens(session=db_session, access_token=access_token, refresh_token=refresh_token)

        return eave_account

    else:
        return None


async def get_existing_eave_account(
    auth_provider: AuthProvider,
    auth_id: str,
    access_token: str,
    refresh_token: str | None,
) -> AccountOrm | None:
    """
    Check for existing account with the given provider and ID.
    Also updates access_token and refresh_token in the database.
    """
    async with eave.core.internal.database.async_session.begin() as db_session:
        eave_account = await AccountOrm.one_or_none(
            session=db_session,
            params=AccountOrm.QueryParams(
                auth_provider=auth_provider,
                auth_id=auth_id,
            ),
        )

        if eave_account:
            # An account exists. Update the saved auth tokens and login date.
            eave_account.last_login = datetime.datetime.utcnow()
            eave_account.set_tokens(session=db_session, access_token=access_token, refresh_token=refresh_token)

    return eave_account


async def create_new_account_and_team(
    request: Request,
    eave_team_name: str,
    user_email: str | None,
    auth_provider: AuthProvider,
    auth_id: str,
    access_token: str,
    refresh_token: str | None,
) -> AccountOrm:
    eave_state = EaveRequestState.load(request=request)
    tracking_cookies = utm_cookies.get_tracking_cookies(request=request)

    async with eave.core.internal.database.async_session.begin() as db_session:
        eave_team = await TeamOrm.create(
            session=db_session,
            name=eave_team_name,
        )

        eave_account = await AccountOrm.create(
            session=db_session,
            team_id=eave_team.id,
            visitor_id=tracking_cookies.visitor_id,
            opaque_utm_params=tracking_cookies.utm_params,
            auth_provider=auth_provider,
            auth_id=auth_id,
            access_token=access_token,
            refresh_token=refresh_token,
            email=user_email,
        )

        await ClientCredentialsOrm.create(
            session=db_session,
            team_id=eave_team.id,
            description="Default client credentials",
            scope=ClientScope.readwrite,
        )

        EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_dataset(dataset_id=eave_team.bq_dataset_id)

        metabase_api_client = MetabaseApiClient.create()
        await metabase_api_client.create_database(name=f"{eave_team.name} ({eave_team.id.hex})", engine="bigquery-cloud-sdk", details={
            "project-id": SHARED_CONFIG.google_cloud_project,
            "service-account-json": CORE_API_APP_CONFIG.metabase_ui_bigquery_accessor_gsa_key_json_b64,
            "dataset-filters-type": "inclusion",
            "dataset-filters-patterns": eave_team.bq_dataset_id,
            "advanced-options": True,
            "use-jvm-timezone": False,
            "include-user-id-and-hash": False,
            "ssl": True,
        })

        await metabase_api_client.create_group(name=f"{eave_team.name} ({eave_team.id.hex})")

    eaveLogger.debug(
        "created new account",
        eave_state.ctx,
        {"eave_account_id": str(eave_account.id), "eave_team_id": str(eave_team.id)},
    )

    await eave.stdlib.analytics.log_event(
        event_name="eave_account_registration",
        event_description="A new account was created",
        event_source="core api oauth",
        eave_account=eave_account.analytics_model,
        eave_team=eave_team.analytics_model,
        ctx=eave_state.ctx,
    )

    return eave_account


async def get_or_create_eave_account(
    request: Request,
    response: Response,
    eave_team_name: str,
    user_email: str | None,
    auth_provider: AuthProvider,
    auth_id: str,
    access_token: str,
    refresh_token: str | None,
) -> AccountOrm:
    eave_account = await get_logged_in_eave_account(
        request=request,
        auth_provider=auth_provider,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    if not eave_account:
        # User is not logged in.
        eave_account = await get_existing_eave_account(
            auth_provider=auth_provider,
            auth_id=auth_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    if not eave_account:
        # Create an account
        eave_account = await create_new_account_and_team(
            request=request,
            eave_team_name=eave_team_name,
            user_email=user_email,
            auth_provider=auth_provider,
            auth_id=auth_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    # Set the cookie in the response headers.
    # This logs the user into their Eave account,
    # or updates the cookies if they were already logged in.
    auth_cookies.set_auth_cookies(
        response=response,
        account_id=eave_account.id,
        team_id=eave_account.team_id,
        access_token=eave_account.access_token,
    )

    set_redirect(response=response, location=DEFAULT_REDIRECT_LOCATION)
    return eave_account


def generate_rand_state() -> str:
    state: str = oauthlib.common.generate_token()
    return state
