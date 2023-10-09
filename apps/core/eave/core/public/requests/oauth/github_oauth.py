import json
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession
from eave.core.internal.orm.github_installation import GithubInstallationOrm

import eave.pubsub_schemas
from eave.stdlib import utm_cookies
from eave.stdlib.auth_cookies import get_auth_cookies
import eave.stdlib.cookies
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.github_api.models import ExternalGithubRepo
from eave.stdlib.github_api.operations.query_repos import QueryGithubRepos
import eave.stdlib.util
import eave.stdlib.analytics
import oauthlib.common
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from eave.core.internal import app_config, database
from eave.core.internal.orm import GithubRepoOrm, AccountOrm
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.core_api.models.integrations import Integration
from eave.core.internal.oauth import state_cookies as oauth_cookies
from eave.stdlib.request_state import EaveRequestState

from eave.stdlib.http_endpoint import HTTPEndpoint
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
        redirect_uri = f"{app_config.eave_public_api_base}/oauth/github/callback"
        state_json = json.dumps({"token": token, "redirect_uri": redirect_uri})
        state = eave.stdlib.util.b64encode(state_json, urlsafe=True)

        authorization_url = f"{app_config.eave_github_app_public_url}/installations/new?state={state}"
        # authorization_url = f"https://github.com/login/oauth/authorize?{qp}"
        response = RedirectResponse(url=authorization_url)

        utm_cookies.set_tracking_cookies(cookies=request.cookies, query_params=request.query_params, response=response)

        oauth_cookies.save_state_cookie(
            response=response,
            state=state,
            provider=_AUTH_PROVIDER,
        )

        return response


class GithubOAuthCallback(HTTPEndpoint):
    auth_provider = _AUTH_PROVIDER
    github_installation_orm: GithubInstallationOrm

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

        self.eave_state = EaveRequestState.load(request=request)

        setup_action = request.query_params.get("setup_action")
        if setup_action not in ["install", "update"]:
            eaveLogger.warning(f"Unexpected github setup_action: {setup_action}", self.eave_state.ctx)

        installation_id = request.query_params.get("installation_id")
        if not installation_id:
            eaveLogger.warning(
                f"github installation_id not provided for action {setup_action}. Cannot proceed.",
                self.eave_state.ctx,
            )
            return shared.cancel_flow(response=self.response)

        self.installation_id = installation_id

        auth_cookies = get_auth_cookies(cookies=request.cookies)

        if not auth_cookies.access_token or not auth_cookies.account_id:
            # This is the case where they're going through the install flow but not logged in.
            # TODO: Once we allow people to install the app before they've created an account, this is where we'd redirect them to the registration flow.
            eaveLogger.warning("Auth cookies not set in GitHub callback, can't proceed.", self.eave_state.ctx)
            return shared.cancel_flow(response=self.response)

        async with database.async_session.begin() as db_session:
            self.eave_account = await AccountOrm.one_or_exception(
                session=db_session, id=auth_cookies.account_id, access_token=auth_cookies.access_token
            )

            self.eave_team = await self.eave_account.get_team(session=db_session)

        shared.set_redirect(
            response=self.response,
            location=shared.DEFAULT_REDIRECT_LOCATION,
        )

        try:
            await self._update_or_create_github_installation()
            await self._sync_github_repos()
        except Exception as e:
            if shared.is_error_response(self.response):
                return self.response
            raise e

        return self.response

    async def _update_or_create_github_installation(
        self,
    ) -> None:
        async with database.async_session.begin() as db_session:
            # try fetch existing github installation
            github_installation_orm = await GithubInstallationOrm.query(
                session=db_session,
                params=GithubInstallationOrm.QueryParams(
                    team_id=self.eave_team.id,
                    github_install_id=self.installation_id,
                ),
            )

            if not github_installation_orm:
                # create new github installation associated with the TeamOrm
                github_installation_orm = await GithubInstallationOrm.create(
                    session=db_session,
                    team_id=self.eave_account.team_id,
                    github_install_id=self.installation_id,
                )

                await eave.stdlib.analytics.log_event(
                    event_name="eave_application_integration",
                    event_description="An integration was added for a team",
                    event_source="core api github oauth",
                    eave_account=self.eave_account.analytics_model,
                    eave_team=self.eave_team.analytics_model,
                    opaque_params={
                        "integration_name": Integration.github.value,
                    },
                    ctx=self.eave_state.ctx,
                )

            elif github_installation_orm.team_id != self.eave_account.team_id:
                eaveLogger.warning(
                    f"A Github integration already exists with github install id {self.installation_id}",
                    self.eave_state.ctx,
                )
                await eave.stdlib.analytics.log_event(
                    event_name="duplicate_integration_attempt",
                    event_source="core api github oauth",
                    eave_account=self.eave_account.analytics_model,
                    eave_team=self.eave_team.analytics_model,
                    opaque_params={"integration": Integration.github},
                    ctx=self.eave_state.ctx,
                )
                shared.set_error_code(response=self.response, error_code=EaveOnboardingErrorCode.already_linked)
                raise Exception("Attempted to link Github integration when one already existed")
            else:
                await eave.stdlib.analytics.log_event(
                    event_name="eave_application_integration_updated",
                    event_description="An integration was re-installed or updated for a team",
                    event_source="core api github oauth",
                    eave_account=self.eave_account.analytics_model,
                    eave_team=self.eave_team.analytics_model,
                    opaque_params={
                        "integration_name": Integration.github.value,
                    },
                    ctx=self.eave_state.ctx,
                )

            self.github_installation_orm = github_installation_orm

    async def _sync_github_repos(self) -> None:
        response = await QueryGithubRepos.perform(
            team_id=self.eave_team.id, origin=EaveApp.eave_api, ctx=self.eave_state.ctx
        )
        repos = response.repos

        async with database.async_session.begin() as db_session:
            # We're grabbing this object fresh from the database so we can update it in this function.
            github_installation_orm = await GithubInstallationOrm.one_or_exception(
                session=db_session,
                team_id=self.eave_team.id,
            )

            if len(repos) > 0:
                # update the GithubInstallation to set the github_owner_login property to the owner of any repository in the list (we happen to get the first one, but they should all be the same).
                if owner := repos[0].owner:
                    github_installation_orm.github_owner_login = owner.login

            for repo in repos:
                await self._create_local_github_repo(repo=repo, db_session=db_session)

    async def _create_local_github_repo(self, repo: ExternalGithubRepo, db_session: AsyncSession) -> None:
        if repo.id is None:
            eaveLogger.error(
                "Malformed repository object",
                self.eave_state.ctx,
            )
            return

        existing_repos = await GithubRepoOrm.query(
            session=db_session,
            params=GithubRepoOrm.QueryParams(
                team_id=self.eave_team.id,
                external_repo_id=repo.id,
            ),
        )
        assert not len(existing_repos) > 1

        existing_repo = existing_repos[0] if len(existing_repos) == 1 else None

        if existing_repo:
            await eave.stdlib.analytics.log_event(
                event_name="repo_already_added",
                event_description="A repo already existed when attempting to save it to the Eave database",
                event_source="core api github oauth",
                eave_account=self.eave_account.analytics_model,
                eave_team=self.eave_team.analytics_model,
                opaque_params={
                    "integration_name": Integration.github.value,
                    "repo_name": repo.name,
                    "repo_id": repo.id,
                },
                ctx=self.eave_state.ctx,
            )
        else:
            await GithubRepoOrm.create(
                session=db_session,
                team_id=self.eave_team.id,
                external_repo_id=repo.id,
                display_name=repo.name,
            )
