import json
import typing

import atlassian
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
import eave.pubsub_schemas
import eave.stdlib
import eave.stdlib.atlassian
import eave.stdlib.core_api
from eave.stdlib import logger
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

import eave.core.internal
import eave.core.internal.oauth.atlassian as oauth_atlassian
import eave.core.internal.oauth.state_cookies as oauth_cookies
import eave.core.public.request_state

from ...http_endpoint import HTTPEndpoint
from . import base, shared

_AUTH_PROVIDER = eave.stdlib.core_api.enums.AuthProvider.atlassian


class AtlassianOAuthAuthorize(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        oauth_session = oauth_atlassian.AtlassianOAuthSession()
        flow_info = oauth_session.oauth_flow_info()
        response = RedirectResponse(url=flow_info.authorization_url)

        oauth_cookies.save_state_cookie(
            response=response,
            state=flow_info.state,
            provider=_AUTH_PROVIDER,
        )
        return response


class AtlassianOAuthCallback(base.BaseOAuthCallback):
    auth_provider = _AUTH_PROVIDER

    async def get(self, request: Request) -> Response:
        await super().get(request=request)

        self.oauth_session = oauth_session = oauth_atlassian.AtlassianOAuthSession(state=self.state)
        oauth_session.fetch_token(code=self.code)
        token = oauth_session.get_token()
        self.atlassian_cloud_id = oauth_session.atlassian_cloud_id

        access_token = token.get("access_token")
        refresh_token = token.get("refresh_token")

        if not access_token or not refresh_token:
            raise eave.stdlib.exceptions.MissingOAuthCredentialsError("atlassian access or refresh token")

        userinfo = oauth_session.get_userinfo()
        if not userinfo.account_id:
            eave.stdlib.logger.warning(
                msg := "atlassian account_id missing; can't create account.", extra=self.eave_state.log_context
            )
            raise eave.stdlib.exceptions.InvalidAuthError(msg)

        resources = oauth_session.get_available_resources()
        resource = next(iter(resources), None)

        if resource and resource.name:
            eave_team_name = resource.name
        else:
            name = userinfo.display_name
            eave_team_name = f"{name}'s Team" if name else "Your Team"

        self.eave_account = await shared.get_or_create_eave_account(
            request=self.request,
            response=self.response,
            eave_team_name=eave_team_name,
            user_email=userinfo.email,
            auth_provider=self.auth_provider,
            auth_id=userinfo.account_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        await self._update_or_create_installation()
        return self.response

    async def _update_or_create_installation(
        self,
    ) -> None:
        oauth_token_encoded = json.dumps(self.oauth_session.get_token())

        async with eave.core.internal.database.async_session.begin() as db_session:
            installation = await AtlassianInstallationOrm.one_or_none(
                session=db_session,
                atlassian_cloud_id=self.atlassian_cloud_id,
            )

            if installation and installation.team_id != self.eave_account.team_id:
                logger.warning(
                    f"An Atlassian integration already exists for atlassian_cloud_id {self.atlassian_cloud_id}",
                    extra=self.eave_state.log_context,
                )
                db_session.add(self.eave_account)
                self.eave_account.team_id = installation.team_id
                return

            if installation and oauth_token_encoded:
                installation.oauth_token_encoded = oauth_token_encoded

            else:
                default_space_key = None

                try:
                    # If the confluence site only has one global space, then use it.
                    confluence_client = atlassian.Confluence(
                        url=self.oauth_session.api_base_url,
                        session=self.oauth_session,
                    )

                    spaces_response = confluence_client.get_all_spaces(space_status="current", space_type="global")
                    spaces_response_json = typing.cast(eave.stdlib.typing.JsonObject, spaces_response)
                    spaces = [
                        eave.stdlib.atlassian.ConfluenceSpace(s)
                        for s in spaces_response_json["results"]
                    ]
                    if len(spaces) == 1 and (first_space := next(iter(spaces), None)):
                        default_space_key = first_space.key

                except Exception:
                    # We aggressively catch any error because this space fetching procedure is a convenience, but failure shouldn't prevent sign-up.
                    eave.stdlib.logger.exception(
                        "error while fetching confluence spaces", extra=self.eave_state.log_context
                    )

                installation = await eave.core.internal.orm.AtlassianInstallationOrm.create(
                    session=db_session,
                    team_id=self.eave_account.team_id,
                    atlassian_cloud_id=self.atlassian_cloud_id,
                    oauth_token_encoded=oauth_token_encoded,
                    confluence_space_key=default_space_key,
                )

                eave_team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                    session=db_session, team_id=self.eave_account.team_id
                )

                eave_team.document_platform = eave.stdlib.core_api.enums.DocumentPlatform.confluence

                eave.stdlib.analytics.log_event(
                    event_name="eave_application_integration",
                    event_description="An integration was added for a team",
                    eave_account_id=self.eave_account.id,
                    eave_team_id=self.eave_account.team_id,
                    eave_visitor_id=self.eave_account.visitor_id,
                    event_source="core api oauth",
                    opaque_params={
                        "integration_name": eave.stdlib.core_api.enums.Integration.atlassian.value,
                        "default_confluence_space_was_used": default_space_key is not None,
                    },
                )
