from dataclasses import dataclass
import oauthlib.oauth2.rfc6749.tokens
import fastapi
from eave.core.internal.config import app_config
import eave.core.internal.orm as eave_orm
import eave.core.internal.database as eave_db
from . import oauth_state, oauth_cookie

@dataclass
class AtlassianOAuthTokenResponse:
    access_token: str
    expires_in: int
    scope: str

async def atlassian_oauth_authorize() -> fastapi.Response:
    oauth_flow_info = get_oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=oauth_flow_info.authorization_url)
    oauth_cookie.save_state_cookie(
        response=response,
        state=oauth_flow_info.state,
        provider=eave_orm.AuthProvider.atlassian,
    )
    return response

async def atlassian_oauth_callback(state: str, code: str, request: fastapi.Request, response: fastapi.Response) -> fastapi.Response:
    expected_oauth_state = oauth_cookie.get_state_cookie(
        request=request,
        provider=eave_orm.AuthProvider.atlassian
    )
    assert state == expected_oauth_state

    oauth_session = build_session(state=expected_oauth_state)

    token: oauthlib.oauth2.rfc6749.tokens.OAuth2Token = oauth_session.fetch_token(
        token_url="https://auth.atlassian.com/oauth/token",
        code=code,
        client_secret=app_config.eave_atlassian_app_client_secret,
    )

    # async with await eave_db.get_session() as session:
    #     eave_orm.AtlassianInstallationOrm.one_or_none()

    #     account_orm = await eave_orm.AccountOrm.one_or_none(
    #         session=session,
    #         auth_provider=eave_orm.AuthProvider.slack,
    #         auth_id=user_id,
    #     )

    #     if account_orm is None:
    #         # If this is a new account, then also create a new team.
    #         # The Team is what is used for integrations, not an individual account.
    #         team = eave_orm.TeamOrm(
    #             name=team_name if (team_name := oauth_data.team.name) else "Your Team",
    #             document_platform=None,
    #         )

    #         session.add(team)
    #         await session.commit()

    #         account_orm = eave_orm.AccountOrm(
    #             team_id=team.id,
    #             auth_provider=eave_orm.AuthProvider.slack,
    #             auth_id=user_id,
    #             oauth_token=oauth_token,
    #         )

    #         session.add(account_orm)
    #     else:
    #         account_orm.oauth_token = oauth_token

    #     # try fetch slack source for eave team
    #     slack_source = await eave_orm.SlackSource.one_or_none(
    #         team_id=account_orm.team_id,
    #         session=session,
    #     )

    #     if slack_source is None:
    #         # create new slack source associated with the TeamOrm
    #         slack_source = eave_orm.SlackSource(
    #             team_id=account_orm.team_id,
    #             slack_team_id=slack_team_id,
    #             bot_token=bot_token,
    #             bot_id=bot_id,
    #         )
    #         session.add(slack_source)
    #     else:
    #         slack_source.slack_team_id = slack_team_id

    #     await session.commit()

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/setup")
    oauth_cookie.delete_state_cookie(response=response, provider=eave_orm.AuthProvider.atlassian)
    return response

def get_oauth_flow_info() -> oauth_state.OauthFlowInfo:
    session = build_session()

    authorization_url, state = session.authorization_url(
        url="https://auth.atlassian.com/authorize",
        audience="api.atlassian.com",
        prompt="consent"
    )

    assert isinstance(authorization_url, str)
    assert isinstance(state, str)
    return oauth_state.OauthFlowInfo(authorization_url=authorization_url, state=state)

