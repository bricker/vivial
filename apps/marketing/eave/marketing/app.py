from typing import Any

import eave.stdlib.api_util as eave_api_util
import eave.stdlib.auth_cookies
import eave.stdlib.core_api
import eave.stdlib.core_api.client as eave_core
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.logging
import eave.stdlib.time
import werkzeug.exceptions
from flask import Flask, Response, make_response, redirect, render_template, request
from werkzeug.wrappers import Response as BaseResponse

from .config import app_config

eave.stdlib.time.set_utc()
eave.stdlib.logging.setup_logging()
eave_core.set_origin(eave_origins.EaveOrigin.eave_www)

app = Flask(__name__)
app.secret_key = app_config.eave_web_session_encryption_key

eave_api_util.add_standard_endpoints(app=app)


def _render_spa(**kwargs: Any) -> str:
    return render_template(
        "index.html.jinja",
        cookie_domain=app_config.eave_cookie_domain,
        api_base=app_config.eave_api_base,
        asset_base=app_config.asset_base,
        analytics_enabled=app_config.analytics_enabled,
        monitoring_enabled=app_config.monitoring_enabled,
        app_env=app_config.app_env,
        app_version=app_config.app_version,
        **kwargs,
    )


@app.route("/dashboard", methods=["GET"])
async def dashboard() -> str:
    return "OK"


@app.route("/dashboard/me/team", methods=["GET"])
async def authed_account_team() -> Response:
    auth_cookies = eave.stdlib.auth_cookies.get_auth_cookies(cookies=request.cookies)

    if not auth_cookies.access_token or not auth_cookies.account_id:
        raise werkzeug.exceptions.Unauthorized()

    eave_response = await eave_core.get_authenticated_account_team_integrations(
        account_id=auth_cookies.account_id,
        access_token=auth_cookies.access_token,
    )

    response = make_response(eave_response.json())
    eave.stdlib.auth_cookies.set_auth_cookies(
        response=response,
        access_token=eave_response.account.access_token,  # In case the access token was refreshed
    )

    return response


@app.route("/dashboard/me/team/integrations/atlassian/update", methods=["POST"])
async def update_atlassian_integration() -> Response:
    auth_cookies = eave.stdlib.auth_cookies.get_auth_cookies(cookies=request.cookies)

    if not auth_cookies.access_token or not auth_cookies.account_id:
        raise werkzeug.exceptions.Unauthorized()

    body = request.get_json()
    confluence_space_key = body["atlassian_integration"]["confluence_space_key"]

    eave_response = await eave_core.update_atlassian_integration(
        account_id=auth_cookies.account_id,
        access_token=auth_cookies.access_token,
        input=eave_ops.UpdateAtlassianInstallation.RequestBody(
            atlassian_integration=eave_ops.UpdateAtlassianInstallationInput(
                confluence_space=confluence_space_key,
            ),
        ),
    )

    response = make_response(eave_response.json())
    eave.stdlib.auth_cookies.set_auth_cookies(
        response=response,
        access_token=eave_response.account.access_token,  # In case the access token was refreshed
    )

    return response


@app.route("/dashboard/logout", methods=["GET"])
async def logout() -> BaseResponse:
    response = redirect(location=app_config.eave_www_base, code=302)
    eave.stdlib.auth_cookies.delete_auth_cookies(response=response)
    return response


@app.route("/access_request", methods=["POST"])
async def api_access_request() -> str:
    body = request.get_json()

    await eave_core.create_access_request(
        input=eave_ops.CreateAccessRequest.RequestBody(
            visitor_id=body["visitor_id"],
            email=body["email"],
            opaque_input=body["opaque_input"],
        ),
    )

    return "OK"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path: str) -> str:
    return _render_spa()
