import datetime
import typing
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import aiohttp
import oauthlib.common
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal.oauth.state_cookies
import eave.pubsub_schemas
import eave.stdlib.config
import eave.stdlib.cookies
import eave.stdlib.exceptions
import eave.stdlib.slack
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.metabase_instance import MetabaseInstanceOrm
from eave.core.internal.orm.team import TeamOrm, bq_dataset_id
from eave.stdlib import auth_cookies
from eave.stdlib.api_util import set_redirect
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.logging import LogContext, eaveLogger
from eave.stdlib.util import ensure_uuid

from . import EAVE_ERROR_CODE_QP, EaveOnboardingErrorCode

DEFAULT_TEAM_NAME = "Your Team"
DEFAULT_REDIRECT_LOCATION = SHARED_CONFIG.eave_dashboard_base_url_public
SIGNUP_REDIRECT_LOCATION = f"{SHARED_CONFIG.eave_dashboard_base_url_public}/signup"


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
    return set_redirect(response=response, location=SHARED_CONFIG.eave_dashboard_base_url_public)


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
    ctx: LogContext,
) -> AccountOrm:
    async with eave.core.internal.database.async_session.begin() as db_session:
        eave_team = await TeamOrm.create(
            session=db_session,
            name=eave_team_name,
        )

        await ClientCredentialsOrm.create(
            session=db_session,
            team_id=eave_team.id,
            description="Default client credentials",
            scope=ClientScope.write,
        )

        await MetabaseInstanceOrm.create(
            session=db_session,
            team_id=eave_team.id,
        )

        eave_account = await AccountOrm.create(
            session=db_session,
            team_id=eave_team.id,
            auth_provider=auth_provider,
            auth_id=auth_id,
            access_token=access_token,
            refresh_token=refresh_token,
            email=user_email,
        )

        EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_dataset(dataset_id=bq_dataset_id(eave_team.id))

    eaveLogger.debug(
        "created new account",
        ctx,
        {"eave_account_id": str(eave_account.id), "eave_team_id": str(eave_team.id)},
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
    ctx: LogContext,
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
            ctx=ctx,
        )

    # Set the cookie in the response headers.
    # This logs the user into their Eave account,
    # or updates the cookies if they were already logged in.
    auth_cookies.set_auth_cookies(
        response=response,
        account_id=eave_account.id,
        access_token=eave_account.access_token,
    )

    set_redirect(response=response, location=DEFAULT_REDIRECT_LOCATION)
    return eave_account


def generate_rand_state() -> str:
    state: str = oauthlib.common.generate_token()
    return state
