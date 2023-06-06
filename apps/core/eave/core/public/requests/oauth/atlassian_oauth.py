# INSTALL URL: https://developer.atlassian.com/console/install/e3c57ac8-296e-4392-b128-4330b1ab2883?signature=9e7204e3d1f2898b576427da60ab2182353879b1173469f1b59e0e9cab271d5439c0ff55d59dab60621d9c871125afe79fac266aa532eb29778a2d751bbe0508&product=confluence&product=jira

import json
import typing

import atlassian
from sqlalchemy import null, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
import eave.pubsub_schemas
import eave.stdlib
import eave.stdlib.atlassian
from eave.stdlib.confluence_api.models import ConfluenceSpace
import eave.stdlib.core_api
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

import eave.core.internal
import eave.core.internal.oauth.atlassian as oauth_atlassian
import eave.core.internal.oauth.state_cookies as oauth_cookies
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.core_api.models.connect import AtlassianProduct
from eave.stdlib.core_api.models.integrations import Integration
from eave.stdlib.core_api.models.team import DocumentPlatform

from ...http_endpoint import HTTPEndpoint
from . import base, shared
from eave.stdlib.confluence_api.operations import GetAvailableSpacesRequest
from eave.core.internal.config import app_config
from eave.stdlib.logging import eaveLogger

_AUTH_PROVIDER = AuthProvider.atlassian


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
            eaveLogger.warning(
                msg := "atlassian account_id missing; can't create account.", extra=self.eave_state.log_context
            )
            raise eave.stdlib.exceptions.InvalidAuthError(msg)

        self.atlassian_resources = oauth_session.get_available_resources()
        self.atlassian_resource = next(iter(self.atlassian_resources), None)

        if self.atlassian_resource and self.atlassian_resource.name:
            eave_team_name = self.atlassian_resource.name
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

        await self._link_connect_installation()
        await self._update_or_create_atlassian_install()

        return self.response

    async def _link_connect_installation(
        self,
    ) -> None:
        # First, check if this team already has a linked ConnectInstallation.
        # If so, nothing else to do.
        async with eave.core.internal.database.async_session.begin() as db_session:
            connect_install = (await ConnectInstallationOrm.query(
                session=db_session,
                product=AtlassianProduct.confluence,
                team_id=self.eave_account.team_id,
            )).first()

            if not connect_install:
                connect_install = await self._get_free_connect_installation(session=db_session)
                if connect_install:
                    # Link the Connect installation with this team
                    connect_install.team_id = self.eave_account.team_id
                    await self._update_eave_team_document_platform(session=db_session)

                    eave.stdlib.analytics.log_event(
                        event_name="eave_application_integration",
                        event_description="An integration was added for a team",
                        eave_account_id=self.eave_account.id,
                        eave_team_id=self.eave_account.team_id,
                        eave_visitor_id=self.eave_account.visitor_id,
                        event_source="core api oauth",
                        opaque_params={
                            "integration_name": Integration.confluence.value,
                            "atlassian_site_name": self.atlassian_resource.name if self.atlassian_resource else None,
                        },
                    )

                else:
                    # TODO: This probably means they didn't complete the connect install, how should we handle this case?
                    eaveLogger.warn("connect install not found", extra=self.eave_state.log_context)

            # TODO: The transaction needs to be closed, because the team ID needs to be saved to the database before we
            # call out to the Confluence API to get the available spaces.

        if connect_install:
            await self._maybe_set_default_confluence_space(connect_installation=connect_install)

    async def _get_free_connect_installation(self, session: AsyncSession) -> ConnectInstallationOrm | None:
        lookup = (
            select(ConnectInstallationOrm)
            .where(ConnectInstallationOrm.team_id.is_(None))
            .where(
                or_(
                    *[
                        ConnectInstallationOrm.org_url == resource.url
                        for resource in self.atlassian_resources
                    ],
                    *[
                        ConnectInstallationOrm.base_url == resource.url # backwards compat
                        for resource in self.atlassian_resources
                    ],
                )
            )
        )

        results = await session.scalars(lookup)
        return results.first()

    async def _update_eave_team_document_platform(self, session: AsyncSession) -> None:
        eave_team = await eave.core.internal.orm.TeamOrm.one_or_exception(
            session=session, team_id=self.eave_account.team_id
        )
        eave_team.document_platform = DocumentPlatform.confluence

    async def _maybe_set_default_confluence_space(self, connect_installation: ConnectInstallationOrm) -> None:
        try:
            async with eave.core.internal.database.async_session.begin() as db_session:
                existing_dest = await ConfluenceDestinationOrm.one_or_none(session=db_session, team_id=self.eave_account.team_id)
                if existing_dest:
                    return

                response = await GetAvailableSpacesRequest.perform(
                    origin=app_config.eave_origin,
                    team_id=self.eave_account.team_id,
                )
                available_spaces = response.confluence_spaces

                if len(available_spaces) == 1:
                    space_key = available_spaces[0].key

                    await ConfluenceDestinationOrm.create(
                        session=db_session,
                        connect_installation_id=connect_installation.id,
                        team_id=self.eave_account.team_id,
                        space_key=space_key,
                    )

                    eave.stdlib.analytics.log_event(
                        event_name="default_confluence_space_used",
                        event_description="A team's confluence space was set automatically",
                        eave_account_id=self.eave_account.id,
                        eave_team_id=self.eave_account.team_id,
                        eave_visitor_id=self.eave_account.visitor_id,
                        event_source="core api oauth",
                        opaque_params={
                            "integration_name": Integration.confluence.value,
                            "atlassian_site_name": self.atlassian_resource.name if self.atlassian_resource else None,
                            "confluence_space_key": space_key,
                        },
                    )
        except Exception as e:
            # Aggressively rescue any type of error, as this is a non-essential procedure.
            eaveLogger.error('Error while getting confluence spaces', exc_info=e, extra=self.eave_state.log_context)

    async def _update_or_create_atlassian_install(self) -> None:
        oauth_token_encoded = json.dumps(self.oauth_session.get_token())

        async with eave.core.internal.database.async_session.begin() as db_session:
            existing_install = await AtlassianInstallationOrm.one_or_none(
                session=db_session,
                atlassian_cloud_id=self.atlassian_cloud_id,
            )

            if existing_install:
                existing_install.oauth_token_encoded = oauth_token_encoded
                return

            if self.atlassian_resource:
                site_name = self.atlassian_resource.name or self.atlassian_resource.url
            else:
                site_name = None

            await eave.core.internal.orm.AtlassianInstallationOrm.create(
                session=db_session,
                team_id=self.eave_account.team_id,
                atlassian_cloud_id=self.atlassian_cloud_id,
                oauth_token_encoded=oauth_token_encoded,
                atlassian_site_name=site_name,
            )
