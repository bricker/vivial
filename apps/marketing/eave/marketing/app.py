from typing import Any

import eave.stdlib.api_util as eave_api_util
import eave.stdlib.cookies
import eave.stdlib.core_api
import eave.stdlib.core_api.client as eave_core
import eave.stdlib.core_api.operations.integrations
import eave.stdlib.requests
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.logging
import eave.stdlib.time
import werkzeug.exceptions
from flask import Flask, Response, make_response, redirect, render_template, request
from werkzeug.wrappers import Response as BaseResponse

from .config import app_config

eave.stdlib.time.set_utc()
eave.stdlib.requests.set_origin(eave_origins.EaveOrigin.eave_www)

app = Flask(__name__)
app.secret_key = app_config.eave_web_session_encryption_key

eave_api_util.add_standard_endpoints(app=app)


@app.route("/_ah/warmup", methods=["GET"])
async def warmup() -> str:
    eave.stdlib.shared_config.preload()
    app_config.preload()
    return "OK"


def _render_spa(**kwargs: Any) -> str:
    return render_template(
        "index.html.jinja",
        cookie_domain=app_config.eave_cookie_domain,
        api_base=app_config.eave_api_base,
        asset_base=app_config.asset_base,
        analytics_enabled=app_config.analytics_enabled,
        monitoring_enabled=app_config.monitoring_enabled,
        app_env=app_config.eave_env,
        app_version=app_config.app_version,
        **kwargs,
    )


@app.route("/authcheck", methods=["GET"])
async def get_auth_state() -> dict[str, bool]:
    auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

    if not auth_cookies.access_token or not auth_cookies.account_id:
        return {"authenticated": False}
    else:
        return {"authenticated": True}


@app.route("/dashboard/me/team", methods=["GET"])
async def authed_account_team() -> Response:
    auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

    if not auth_cookies.access_token or not auth_cookies.account_id:
        raise werkzeug.exceptions.Unauthorized()

    eave_response = await eave_core.get_authenticated_account_team_integrations(
        account_id=auth_cookies.account_id,
        access_token=auth_cookies.access_token,
    )

    return _clean_response(eave_response)


@app.route("/dashboard/me/team/integrations/atlassian/update", methods=["POST"])
async def update_atlassian_integration() -> Response:
    auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

    if not auth_cookies.access_token or not auth_cookies.account_id:
        raise werkzeug.exceptions.Unauthorized()

    body = request.get_json()
    confluence_space_key = body["atlassian_integration"]["confluence_space_key"]

    await eave_core.update_atlassian_integration(
        account_id=auth_cookies.account_id,
        access_token=auth_cookies.access_token,
        input=eave.stdlib.core_api.operations.integrations.UpdateAtlassianInstallation.RequestBody(
            atlassian_integration=eave.stdlib.core_api.operations.integrations.UpdateAtlassianInstallationInput(
                confluence_space_key=confluence_space_key,
            ),
        ),
    )

    eave_response = await eave_core.get_authenticated_account_team_integrations(
        account_id=auth_cookies.account_id,
        access_token=auth_cookies.access_token,
    )

    return _clean_response(eave_response)


@app.route("/dashboard/logout", methods=["GET"])
async def logout() -> BaseResponse:
    response = redirect(location=app_config.eave_www_base, code=302)
    eave.stdlib.cookies.delete_auth_cookies(response=response)
    return response


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path: str) -> str:
    return _render_spa()


def _clean_response(eave_response: eave_ops.GetAuthenticatedAccountTeamIntegrations.ResponseBody) -> Response:
    # TODO: The server should send this back in a header or a cookie so we don't have to delete it here.
    access_token = eave_response.account.access_token
    del eave_response.account.access_token

    # TODO: The server doesn't need to send these to the web app.
    if eave_response.integrations.atlassian:
        del eave_response.integrations.atlassian.oauth_token_encoded
    if eave_response.integrations.slack:
        del eave_response.integrations.slack.bot_token

    response = make_response(eave_response.json())

    eave.stdlib.cookies.set_auth_cookies(
        response=response,
        access_token=access_token,  # In case the access token was refreshed
    )

    # TODO: Forward cookies from server to client
    return response
