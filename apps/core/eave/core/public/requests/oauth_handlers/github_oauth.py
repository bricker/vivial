import json
import typing
import urllib.parse

import eave.core.internal
import eave.core.internal.orm
import eave.core.public.requests.util
import eave.pubsub_schemas
import eave.stdlib
import eave.stdlib.core_api
import fastapi
import oauthlib.common
from eave.core.internal.oauth import state_cookies as oauth_cookies

from . import shared

_AUTH_PROVIDER = eave.stdlib.core_api.enums.AuthProvider.github
_special_redirect_uri_cookie = "ev_github_oauth_redirect_uri"


async def github_oauth_authorize() -> fastapi.Response:
    # random value for verifying request wasnt tampered with via CSRF
    token: str = oauthlib.common.generate_token()

    # For GitHub, there is a problem: The combined Installation + Authorization flow doesn't allow us
    # to specify a redirect_uri; it chooses the first one configured. So it always redirects to eave.fyi,
    # which makes it practically impossible to test in development (without some proxy configuration).
    # So instead, we're going to set a special cookie and read it on the other side (callback), and redirect if necessary.
    # https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app#generating-a-user-access-token-when-a-user-installs-your-app
    redirect_uri = f"{eave.core.internal.app_config.eave_api_base}/oauth/github/callback"
    state_json = json.dumps({"token": token, "redirect_uri": redirect_uri})
    state = eave.stdlib.util.b64encode(state_json, urlsafe=True)

    authorization_url = f"https://github.com/apps/eave-fyi/installations/new?state={state}"
    # authorization_url = f"https://github.com/login/oauth/authorize?{qp}"
    response = fastapi.responses.RedirectResponse(url=authorization_url)
    oauth_cookies.save_state_cookie(
        response=response,
        state=state,
        provider=_AUTH_PROVIDER,
    )

    return response


async def github_oauth_callback(
    request: fastapi.Request,
    response: fastapi.Response,
    state: str,
    installation_id: typing.Optional[str] = None,
    setup_action: typing.Optional[str] = None,
    code: typing.Optional[str] = None,
    error: typing.Optional[str] = None,
    error_description: typing.Optional[str] = None,
) -> fastapi.Response:
    # Because of the GitHub redirect_uri issue described in this file, we need to get the redirect_uri from state,
    # and redirect if it's on a different host.
    # Reminder that in this scenario, the cookies from your local environment won't be available here (because we're probably at eave.fyi)
    state_decoded = json.loads(eave.stdlib.util.b64decode(state, urlsafe=True))
    if redirect_uri := state_decoded.get("redirect_uri"):
        url = urllib.parse.urlparse(redirect_uri)
        if url.hostname != request.url.hostname:
            return shared.set_redirect(response=response, location=redirect_uri)

    shared.verify_oauth_state_or_exception(
        state=state, auth_provider=_AUTH_PROVIDER, request=request, response=response
    )

    eave_state = eave.core.public.requests.util.get_eave_state(request=request)
    auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

    # TODO: Allow GitHub as real auth provider.
    # For GitHub, we don't actually do OAuth (despite the name and location of this file), so if they
    # arrive here then they're expect to be already logged in.
    if not auth_cookies.access_token or not auth_cookies.account_id:
        eave.stdlib.logger.error(
            "Auth cookies not set in GitHub callback, can't proceed.", extra=eave_state.log_context
        )
        return shared.cancel_flow(response=response)

    async with eave.core.internal.database.async_session.begin() as db_session:
        eave_account = await eave.core.internal.orm.AccountOrm.one_or_exception(
            session=db_session, id=auth_cookies.account_id, access_token=auth_cookies.access_token
        )

    if setup_action != "install":
        eave.stdlib.logger.warn(f"Unexpected github setup_action: {setup_action}", extra=eave_state.log_context)

    if not installation_id:
        eave.stdlib.logger.warn(
            f"github installation_id not provided for action {setup_action}. Cannot proceed.",
            extra=eave_state.log_context,
        )
        return shared.cancel_flow(response=response)

    await _update_or_create_github_installation(
        eave_state=eave_state,
        eave_account=eave_account,
        github_install_id=installation_id,
    )

    return shared.set_redirect(response=response, location=f"{eave.core.internal.app_config.eave_www_base}/dashboard")


async def _update_or_create_github_installation(
    eave_state: eave.core.public.requests.util.EaveRequestState,
    eave_account: eave.core.internal.orm.AccountOrm,
    github_install_id: str,
) -> None:
    async with eave.core.internal.database.async_session.begin() as db_session:
        # try fetch existing github installation
        github_installation = await eave.core.internal.orm.GithubInstallationOrm.one_or_none(
            session=db_session,
            github_install_id=github_install_id,
        )

        if github_installation and github_installation.team_id != eave_account.team_id:
            msg = f"A Github integration already exists with github install id {github_install_id}"
            await eave_state.add_note(msg)
            eave.stdlib.logger.warning(msg, extra=eave_state.log_context)
            return

        else:
            # create new github installation associated with the TeamOrm
            github_installation = await eave.core.internal.orm.GithubInstallationOrm.create(
                session=db_session,
                team_id=eave_account.team_id,
                github_install_id=github_install_id,
            )

    eave.stdlib.analytics.log_event(
        event_name="eave_application_integration",
        event_description="An integration was added for a team",
        eave_account_id=eave_account.id,
        eave_team_id=eave_account.team_id,
        eave_visitor_id=eave_account.visitor_id,
        event_source="core api oauth",
        opaque_params={
            "integration_name": eave.stdlib.core_api.enums.Integration.github.value,
        },
    )
