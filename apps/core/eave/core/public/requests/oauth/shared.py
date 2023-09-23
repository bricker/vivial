import http
import re
import typing
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import eave.pubsub_schemas
from eave.stdlib import auth_cookies, utm_cookies
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.logging import eaveLogger
from eave.stdlib.request_state import EaveRequestState
import eave.stdlib.slack
import eave.stdlib.cookies
import eave.stdlib.analytics
import eave.stdlib.exceptions
import eave.stdlib.config
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal
import eave.core.internal.oauth.state_cookies
import eave.core.internal.orm
from . import EaveOnboardingErrorCode, EAVE_ERROR_CODE_QP

DEFAULT_REDIRECT_LOCATION = f"{eave.core.internal.app_config.eave_public_www_base}/dashboard"


def verify_oauth_state_or_exception(
    state: typing.Optional[str],
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
    response.headers["Location"] = location
    response.status_code = http.HTTPStatus.TEMPORARY_REDIRECT
    return response


def set_error_code(response: Response, error_code: EaveOnboardingErrorCode) -> Response:
    location_header = response.headers["Location"]
    location = urlparse(location_header)
    qs = parse_qs(location.query)
    qs.update({EAVE_ERROR_CODE_QP: [error_code.value]})
    qs_updated = urlencode(qs, doseq=True)
    location = location._replace(query=qs_updated)
    return set_redirect(response=response, location=urlunparse(location))


def cancel_flow(response: Response) -> Response:
    return set_redirect(response=response, location=eave.core.internal.app_config.eave_public_www_base)


async def get_logged_in_eave_account(
    request: Request,
    auth_provider: AuthProvider,
    access_token: str,
    refresh_token: typing.Optional[str],
) -> typing.Optional[eave.core.internal.orm.AccountOrm]:
    """
    Check if the user is logged in, and if so, get the account associated with the provided access token and account ID.
    """
    auth_cookies_ = auth_cookies.get_auth_cookies(cookies=request.cookies)

    if auth_cookies_.access_token and auth_cookies_.account_id:
        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_account = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session, id=auth_cookies_.account_id, access_token=auth_cookies_.access_token
            )

            if eave_account.auth_provider == auth_provider:
                # If the user is logged in through this provider, then take this opportunity to update the access and refresh tokens.
                if access_token:
                    eave_account.access_token = access_token

                if refresh_token:
                    eave_account.refresh_token = refresh_token

        return eave_account

    else:
        return None


async def get_existing_eave_account(
    auth_provider: AuthProvider,
    auth_id: str,
    access_token: str,
    refresh_token: typing.Optional[str],
) -> typing.Optional[eave.core.internal.orm.AccountOrm]:
    """
    Check for existing account with the given provider and ID.
    Also updates access_token and refresh_token in the database.
    """
    async with eave.core.internal.database.async_session.begin() as db_session:
        eave_account = await eave.core.internal.orm.AccountOrm.one_or_none(
            session=db_session,
            auth_provider=auth_provider,
            auth_id=auth_id,
        )

        if eave_account:
            # An account exists. Update the saved auth tokens.
            if access_token:
                eave_account.access_token = access_token
            if refresh_token:
                eave_account.refresh_token = refresh_token

    return eave_account


async def create_new_account_and_team(
    request: Request,
    eave_team_name: str,
    user_email: str | None,
    auth_provider: AuthProvider,
    auth_id: str,
    access_token: str,
    refresh_token: typing.Optional[str],
) -> eave.core.internal.orm.AccountOrm:
    eave_state = EaveRequestState.load(request=request)
    tracking_cookies = utm_cookies.get_tracking_cookies(cookies=request.cookies)

    async with eave.core.internal.database.async_session.begin() as db_session:
        eave_team = await eave.core.internal.orm.TeamOrm.create(
            session=db_session,
            name=eave_team_name,
            document_platform=None,
        )

        eave_account = await eave.core.internal.orm.AccountOrm.create(
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

    try:
        # TODO: This should happen in a pubsub subscriber on the "eave_account_registration" event.
        # Notify #sign-ups Slack channel.

        if user_email and re.search("@eave.fyi$", user_email):
            channel_id = "C04GDPU3B5Z"  # #bot-testing in eave slack
        else:
            channel_id = "C04HH2N08LD"  # #sign-ups in eave slack

        slack_client = eave.stdlib.slack.get_authenticated_eave_system_slack_client()
        slack_response = await slack_client.chat_postMessage(
            channel=channel_id,
            text="Someone registered for Eave!",
        )

        await slack_client.chat_postMessage(
            channel=channel_id,
            thread_ts=slack_response.get("ts"),
            text=(
                f"Auth Provider: `{auth_provider.value}`\n"
                f"Email: `{user_email}`\n"
                f"Account ID: `{eave_account.id}`\n"
                f"Visitor ID: `{eave_account.visitor_id}`\n"
                f"Eave Team Name: `{eave_team.name}`\n"
                f"UTM Params:\n"
                f"```{eave_account.opaque_utm_params}```"
            ),
        )
    except Exception as e:
        eaveLogger.exception(e, eave_state.ctx)

    return eave_account


async def get_or_create_eave_account(
    request: Request,
    response: Response,
    eave_team_name: str,
    user_email: typing.Optional[str],
    auth_provider: AuthProvider,
    auth_id: str,
    access_token: str,
    refresh_token: typing.Optional[str],
) -> eave.core.internal.orm.AccountOrm:
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
        access_token=eave_account.access_token,
    )

    set_redirect(response=response, location=DEFAULT_REDIRECT_LOCATION)
    return eave_account
