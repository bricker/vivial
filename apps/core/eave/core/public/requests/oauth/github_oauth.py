import json
import urllib.parse

import eave.pubsub_schemas
import eave.stdlib.cookies
import eave.stdlib.util
import eave.stdlib.analytics
import oauthlib.common
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

import eave.core.internal
import eave.core.internal.orm
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.core_api.models.integrations import Integration
from eave.core.internal.oauth import state_cookies as oauth_cookies
from eave.stdlib.request_state import EaveRequestState

from ...http_endpoint import HTTPEndpoint
from . import EaveOnboardingErrorCode, shared
from eave.stdlib.logging import eaveLogger

_AUTH_PROVIDER = AuthProvider.github


class GithubOAuthAuthorize(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
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

        authorization_url = f"{eave.core.internal.app_config.eave_github_app_public_url}/installations/new?state={state}"
        # authorization_url = f"https://github.com/login/oauth/authorize?{qp}"
        response = RedirectResponse(url=authorization_url)
        oauth_cookies.save_state_cookie(
            response=response,
            state=state,
            provider=_AUTH_PROVIDER,
        )

        return response


class GithubOAuthCallback(HTTPEndpoint):
    auth_provider = _AUTH_PROVIDER

    async def get(
        self,
        request: Request,
    ) -> Response:
        self.response = Response()
        self.state = state = request.query_params["state"]

        # Because of the GitHub redirect_uri issue described in this file, we need to get the redirect_uri from state,
        # and redirect if it's on a different host.
        # Reminder that in this scenario, the cookies from your local environment won't be available here (because we're probably at eave.fyi)
        state_decoded = json.loads(eave.stdlib.util.b64decode(state, urlsafe=True))
        if redirect_uri := state_decoded.get("redirect_uri"):
            url = urllib.parse.urlparse(redirect_uri)
            if url.hostname != request.url.hostname:
                qp = urllib.parse.urlencode(request.query_params)
                location = f"{redirect_uri}?{qp}"
                return shared.set_redirect(response=self.response, location=location)

        shared.verify_oauth_state_or_exception(
            state=self.state, auth_provider=_AUTH_PROVIDER, request=request, response=self.response
        )

        # code = request.query_params.get("code")
        # error = request.query_params.get("error")
        # error_description = request.query_params.get("error_description")

        self.eave_state = eave_state = EaveRequestState.load(request=request)

        setup_action = request.query_params.get("setup_action")
        if setup_action != "install":
            eaveLogger.warning(f"Unexpected github setup_action: {setup_action}", eave_state.ctx)

        installation_id = request.query_params.get("installation_id")
        if not installation_id:
            eaveLogger.warning(
                f"github installation_id not provided for action {setup_action}. Cannot proceed.",
                eave_state.ctx,
            )
            return shared.cancel_flow(response=self.response)

        self.installation_id = installation_id

        auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

        # TODO: Allow GitHub as real auth provider.
        # For GitHub, we don't actually do OAuth (despite the name and location of this file), so if they
        # arrive here then they're expect to be already logged in.
        if not auth_cookies.access_token or not auth_cookies.account_id:
            eaveLogger.warning("Auth cookies not set in GitHub callback, can't proceed.", eave_state.ctx)
            return shared.cancel_flow(response=self.response)

        async with eave.core.internal.database.async_session.begin() as db_session:
            self.eave_account = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session, id=auth_cookies.account_id, access_token=auth_cookies.access_token
            )

        shared.set_redirect(
            response=self.response,
            location=shared.DEFAULT_REDIRECT_LOCATION,
        )
        await self._update_or_create_github_installation()
        return self.response

    async def _update_or_create_github_installation(
        self,
    ) -> None:
        async with eave.core.internal.database.async_session.begin() as db_session:
            # try fetch existing github installation
            github_installation = await eave.core.internal.orm.GithubInstallationOrm.one_or_none(
                session=db_session,
                github_install_id=self.installation_id,
            )

            if github_installation and github_installation.team_id != self.eave_account.team_id:
                eaveLogger.warning(
                    f"A Github integration already exists with github install id {self.installation_id}",
                    self.eave_state.ctx,
                )
                eave.stdlib.analytics.log_event(
                    event_name="duplicate_integration_attempt",
                    eave_account_id=self.eave_account.id,
                    eave_team_id=self.eave_account.team_id,
                    opaque_params={"integration": Integration.github},
                )
                shared.set_error_code(response=self.response, error_code=EaveOnboardingErrorCode.already_linked)
                return

            else:
                # create new github installation associated with the TeamOrm
                github_installation = await eave.core.internal.orm.GithubInstallationOrm.create(
                    session=db_session,
                    team_id=self.eave_account.team_id,
                    github_install_id=self.installation_id,
                )

        eave.stdlib.analytics.log_event(
            event_name="eave_application_integration",
            event_description="An integration was added for a team",
            eave_account_id=self.eave_account.id,
            eave_team_id=self.eave_account.team_id,
            eave_visitor_id=self.eave_account.visitor_id,
            event_source="core api oauth",
            opaque_params={
                "integration_name": Integration.github.value,
            },
        )
