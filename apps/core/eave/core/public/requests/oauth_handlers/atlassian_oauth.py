import json
import typing

import atlassian
import eave.core.internal
import eave.core.internal.oauth.atlassian as oauth_atlassian
import eave.core.internal.oauth.state_cookies as oauth_cookies
import eave.core.internal.orm
import eave.core.public.requests.util
import eave.pubsub_schemas
import eave.stdlib
import eave.stdlib.atlassian
import eave.stdlib.core_api
import fastapi
from eave.stdlib import logger

from . import shared

_AUTH_PROVIDER = eave.stdlib.core_api.enums.AuthProvider.atlassian


async def atlassian_oauth_authorize(request: fastapi.Request) -> fastapi.Response:
    oauth_session = oauth_atlassian.AtlassianOAuthSession()
    flow_info = oauth_session.oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=flow_info.authorization_url)

    oauth_cookies.save_state_cookie(
        response=response,
        state=flow_info.state,
        provider=_AUTH_PROVIDER,
    )
    return response


async def atlassian_oauth_callback(
    request: fastapi.Request,
    response: fastapi.Response,
    state: str,
    code: typing.Optional[str] = None,
    error: typing.Optional[str] = None,
    error_description: typing.Optional[str] = None,
) -> fastapi.Response:
    shared.verify_oauth_state_or_exception(
        state=state, auth_provider=_AUTH_PROVIDER, request=request, response=response
    )

    eave_state = eave.core.public.requests.util.get_eave_state(request=request)

    if error or not code:
        eave.stdlib.logger.warning(
            f"Error response from Atlassian OAuth flow or code missing. {error}: {error_description}",
            extra=eave_state.log_context,
        )
        shared.set_redirect(response=response, location=eave.core.internal.app_config.eave_www_base)
        return response

    oauth_session = oauth_atlassian.AtlassianOAuthSession(state=state)
    oauth_session.fetch_token(code=code)
    token = oauth_session.get_token()
    atlassian_cloud_id = oauth_session.atlassian_cloud_id

    access_token = token.get("access_token")
    refresh_token = token.get("refresh_token")

    if not access_token or not refresh_token:
        eave.stdlib.logger.warning(msg := "missing tokens.", extra=eave_state.log_context)
        raise eave.stdlib.exceptions.InvalidAuthError(msg)

    userinfo = oauth_session.get_userinfo()
    if not userinfo.account_id:
        eave.stdlib.logger.warning(
            msg := "atlassian account_id missing; can't create account.", extra=eave_state.log_context
        )
        raise eave.stdlib.exceptions.InvalidAuthError(msg)

    resources = oauth_session.get_available_resources()
    resource = next(iter(resources), None)

    if resource and resource.name:
        eave_team_name = resource.name
    else:
        name = userinfo.display_name
        eave_team_name = f"{name}'s Team" if name else "Your Team"

    eave_account = await shared.get_or_create_eave_account(
        request=request,
        response=response,
        eave_team_name=eave_team_name,
        user_email=userinfo.email,
        auth_provider=_AUTH_PROVIDER,
        auth_id=userinfo.account_id,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    await _update_or_create_installation(
        eave_state=eave_state,
        eave_account=eave_account,
        atlassian_cloud_id=atlassian_cloud_id,
        oauth_session=oauth_session,
    )

    return response


async def _update_or_create_installation(
    eave_state: eave.core.public.requests.util.EaveRequestState,
    eave_account: eave.core.internal.orm.AccountOrm,
    atlassian_cloud_id: str,
    oauth_session: oauth_atlassian.AtlassianOAuthSession,
) -> None:
    oauth_token_encoded = json.dumps(oauth_session.get_token())

    async with eave.core.internal.database.async_session.begin() as db_session:
        installation = await eave.core.internal.orm.AtlassianInstallationOrm.one_or_none(
            session=db_session,
            atlassian_cloud_id=atlassian_cloud_id,
        )

        if installation and installation.team_id != eave_account.team_id:
            await eave_state.add_note(
                msg := f"An Atlassian integration already exists for atlassian_cloud_id {atlassian_cloud_id}"
            )
            logger.warning(msg, extra=eave_state.log_context)
            return

        if installation and oauth_token_encoded:
            installation.oauth_token_encoded = oauth_token_encoded

        else:
            default_space_key = None

            try:
                # If the confluence site only has one global space, then use it.
                confluence_client = atlassian.Confluence(
                    url=oauth_session.api_base_url,
                    session=oauth_session,
                )

                spaces_response = confluence_client.get_all_spaces(space_status="current", space_type="global")
                spaces_response_json = typing.cast(eave.stdlib.util.JsonObject, spaces_response)
                spaces = [
                    eave.stdlib.atlassian.ConfluenceSpace(s, oauth_session.confluence_context)
                    for s in spaces_response_json["results"]
                ]
                if len(spaces) == 1 and (first_space := next(iter(spaces), None)):
                    default_space_key = first_space.key

            except Exception as e:
                # We aggressively catch any error because this space fetching procedure is a convenience, but failure shouldn't prevent sign-up.
                eave.stdlib.logger.error(
                    "error while fetching confluence spaces", exc_info=e, extra=eave_state.log_context
                )

            installation = await eave.core.internal.orm.AtlassianInstallationOrm.create(
                session=db_session,
                team_id=eave_account.team_id,
                atlassian_cloud_id=atlassian_cloud_id,
                oauth_token_encoded=oauth_token_encoded,
                confluence_space_key=default_space_key,
            )

            eave.stdlib.analytics.log_event(
                event_name="eave_application_integration",
                event_description="An integration was added for a team",
                eave_account_id=eave_account.id,
                eave_team_id=eave_account.team_id,
                eave_visitor_id=eave_account.visitor_id,
                event_source="core api oauth",
                opaque_params={
                    "integration_name": eave.stdlib.core_api.enums.Integration.atlassian.value,
                    "default_confluence_space_was_used": default_space_key is not None,
                },
            )
