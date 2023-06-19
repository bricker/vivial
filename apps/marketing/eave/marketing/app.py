import json
from typing import Any

import eave.stdlib.api_util as eave_api_util
from eave.stdlib.confluence_api.operations import GetAvailableSpacesRequest
import eave.stdlib.cookies
from eave.stdlib.core_api.models.team import ConfluenceDestinationInput
import eave.stdlib.core_api.operations.account as account
from eave.stdlib.core_api.operations.team import UpsertConfluenceDestinationAuthedRequest
import eave.stdlib.requests
import eave.stdlib.logging
import eave.stdlib.time
import werkzeug.exceptions
from flask import Flask, Response, redirect, render_template, request
from werkzeug.wrappers import Response as BaseResponse
from eave.stdlib.typing import JsonObject
from .config import app_config

eave.stdlib.time.set_utc()

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
async def get_auth_state() -> Response:
    auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

    response_body: JsonObject
    if not auth_cookies.access_token or not auth_cookies.account_id:
        response_body = {"authenticated": False}
    else:
        response_body = {"authenticated": True}

    return _json_response(body=response_body)


@app.route("/dashboard/me/team", methods=["GET"])
async def authed_account_team() -> Response:
    auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

    if not auth_cookies.access_token or not auth_cookies.account_id:
        raise werkzeug.exceptions.Unauthorized()

    eave_response = await account.GetAuthenticatedAccountTeamIntegrations.perform(
        origin=app_config.eave_origin,
        account_id=auth_cookies.account_id,
        access_token=auth_cookies.access_token,
    )

    return _clean_response(eave_response)


@app.route("/dashboard/me/team/destinations/confluence/spaces/query", methods=["GET"])
async def get_available_spaces() -> Response:
    auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

    if not auth_cookies.access_token or not auth_cookies.account_id:
        raise werkzeug.exceptions.Unauthorized()

    # HACK: Just using this endpoint to validate the access token
    team_response = await account.GetAuthenticatedAccountTeamIntegrations.perform(
        origin=app_config.eave_origin,
        account_id=auth_cookies.account_id,
        access_token=auth_cookies.access_token,
    )

    spaces_response = await GetAvailableSpacesRequest.perform(
        origin=app_config.eave_origin,
        team_id=team_response.team.id,
    )

    return _json_response(body=spaces_response.json())


@app.route("/dashboard/me/team/destinations/confluence/upsert", methods=["POST"])
async def upsert_confluence_destination() -> Response:
    auth_cookies = eave.stdlib.cookies.get_auth_cookies(cookies=request.cookies)

    if not auth_cookies.access_token or not auth_cookies.account_id:
        raise werkzeug.exceptions.Unauthorized()

    body = request.get_json()
    confluence_space_key = body["confluence_destination"]["space_key"]

    await UpsertConfluenceDestinationAuthedRequest.perform(
        origin=app_config.eave_origin,
        account_id=auth_cookies.account_id,
        access_token=auth_cookies.access_token,
        input=UpsertConfluenceDestinationAuthedRequest.RequestBody(
            confluence_destination=ConfluenceDestinationInput(
                space_key=confluence_space_key,
            ),
        ),
    )

    eave_response = await account.GetAuthenticatedAccountTeamIntegrations.perform(
        origin=app_config.eave_origin,
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


def _clean_response(eave_response: account.GetAuthenticatedAccountTeamIntegrations.ResponseBody) -> Response:
    # TODO: The server should send this back in a header or a cookie so we don't have to delete it here.
    access_token = eave_response.account.access_token
    del eave_response.account.access_token

    response = _json_response(body=eave_response.json())

    eave.stdlib.cookies.set_auth_cookies(
        response=response,
        access_token=access_token,  # In case the access token was refreshed
    )

    # TODO: Forward cookies from server to client
    return response


def _json_response(body: JsonObject | str) -> Response:
    if not isinstance(body, str):
        body = json.dumps(body)

    return Response(
        response=body,
        mimetype="application/json",
    )
