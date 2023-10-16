import json
import time
from typing import Any
from eave.stdlib.auth_cookies import AuthCookies, delete_auth_cookies, get_auth_cookies, set_auth_cookies

import eave.stdlib.cookies
from eave.stdlib.core_api.models.github_repos import GithubRepoUpdateInput
from eave.stdlib.core_api.operations import BaseResponseBody
import eave.stdlib.core_api.operations.account as account
import eave.stdlib.core_api.operations.team as team
import eave.stdlib.core_api.operations.github_repos as github_repos
import eave.stdlib.core_api.operations.github_documents as github_documents
from eave.stdlib.core_api.models.github_documents import GithubDocument, GithubDocumentsQueryInput, Status
from eave.stdlib.github_api.operations.query_repos import QueryGithubRepos
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.util import ensure_uuid, unwrap

from eave.stdlib.endpoints import status_payload
import eave.stdlib.requests
import eave.stdlib.logging
import eave.stdlib.time
import werkzeug.exceptions
from flask import Flask, Response, make_response, redirect, render_template, request
from werkzeug.wrappers import Response as BaseResponse
from eave.stdlib.typing import JsonArray, JsonObject
from eave.stdlib.utm_cookies import set_tracking_cookies
from .config import app_config
from eave.stdlib.config import shared_config
from eave.stdlib.logging import eaveLogger

eave.stdlib.time.set_utc()

app = Flask(__name__)
app.secret_key = app_config.eave_web_session_encryption_key


@app.get("/status")
def status() -> str:
    model = status_payload()
    return model.json()


@app.route("/_ah/warmup", methods=["GET"])
async def warmup() -> str:
    shared_config.preload()
    app_config.preload()
    return "OK"


@app.route("/_ah/start", methods=["GET"])
async def start() -> str:
    return "OK"


@app.route("/_ah/stop", methods=["GET"])
async def stop() -> str:
    return "OK"


def _render_spa(**kwargs: Any) -> str:
    return render_template(
        "index.html.jinja",
        cookie_domain=app_config.eave_cookie_domain,
        api_base=app_config.eave_public_api_base,
        asset_base=app_config.asset_base,
        analytics_enabled=app_config.analytics_enabled,
        app_env=app_config.eave_env,
        app_version=app_config.app_version,
        **kwargs,
    )


@app.route("/authcheck", methods=["GET"])
async def get_auth_state() -> Response:
    auth_cookies = get_auth_cookies(cookies=request.cookies)

    response_body: JsonObject
    if not auth_cookies.access_token or not auth_cookies.account_id or not auth_cookies.team_id:
        response_body = {"authenticated": False}
    else:
        response_body = {"authenticated": True}

    return _json_response(body=response_body)


@app.route("/dashboard/me", methods=["GET", "POST"])
async def get_user() -> Response:
    auth_cookies = get_auth_cookies(cookies=request.cookies)
    _assert_auth(auth_cookies)

    eave_response = await account.GetAuthenticatedAccount.perform(
        origin=app_config.eave_origin,
        team_id=ensure_uuid(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
    )

    return _make_response(eave_response)


@app.route("/dashboard/team", methods=["GET", "POST"])
async def get_team() -> Response:
    auth_cookies = get_auth_cookies(cookies=request.cookies)
    _assert_auth(auth_cookies)

    eave_response = await team.GetTeamRequest.perform(
        origin=app_config.eave_origin,
        team_id=unwrap(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
    )

    return _make_response(eave_response)


@app.route("/dashboard/team/repos", methods=["GET", "POST"])
async def get_team_repos() -> Response:
    auth_cookies = get_auth_cookies(cookies=request.cookies)
    _assert_auth(auth_cookies)

    try:
        eave_response = await github_repos.GetGithubReposRequest.perform(
            origin=app_config.eave_origin,
            team_id=unwrap(auth_cookies.team_id),
            account_id=ensure_uuid(auth_cookies.account_id),
            access_token=unwrap(auth_cookies.access_token),
            input=github_repos.GetGithubReposRequest.RequestBody(repos=None),
        )
    except Exception as e:
        eaveLogger.exception(e)
        return _json_response(body={"repos": []})

    response = _make_response(eave_response)

    internal_repo_list = eave_response.repos
    if len(internal_repo_list) == 0:
        _set_json_response_body(response, {"repos": []})
        return response

    external_response = await QueryGithubRepos.perform(
        origin=app_config.eave_origin, team_id=unwrap(auth_cookies.team_id)
    )
    external_repo_list = external_response.repos
    external_repo_map = {repo.id: repo for repo in external_repo_list if repo.id is not None}
    merged_repo_list: JsonArray = []

    for repo in internal_repo_list:
        repo_id = repo.external_repo_id
        if repo_id in external_repo_map:
            jsonRepo = json.loads(repo.json())
            jsonRepo["external_repo_data"] = json.loads(external_repo_map[repo_id].json())
            merged_repo_list.append(jsonRepo)

    _set_json_response_body(response, {"repos": merged_repo_list})
    return response


@app.route("/dashboard/team/repos/update", methods=["POST"])
async def update_team_repos() -> Response:
    auth_cookies = get_auth_cookies(cookies=request.cookies)
    _assert_auth(auth_cookies)

    body = request.get_json()
    repos: list[GithubRepoUpdateInput] = body["repos"]

    eave_response = await github_repos.UpdateGithubReposRequest.perform(
        origin=app_config.eave_origin,
        team_id=unwrap(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
        input=github_repos.UpdateGithubReposRequest.RequestBody(repos=repos),
    )

    return _make_response(eave_response)


@app.route("/dashboard/team/documents", methods=["POST"])
async def get_team_documents() -> Response:
    auth_cookies = get_auth_cookies(cookies=request.cookies)
    _assert_auth(auth_cookies)

    body = request.get_json()
    document_type = body["document_type"]

    eave_response = await github_documents.GetGithubDocumentsRequest.perform(
        origin=app_config.eave_origin,
        team_id=unwrap(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
        input=github_documents.GetGithubDocumentsRequest.RequestBody(
            query_params=GithubDocumentsQueryInput(type=document_type)
        ),
    )

    # sort documents in place
    eave_response.documents.sort(key=_document_rank)
    return _make_response(eave_response)


@app.route("/dashboard/logout", methods=["GET"])
async def logout() -> BaseResponse:
    response = redirect(location=app_config.eave_public_www_base, code=302)
    delete_auth_cookies(response=response)
    return response


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path: str) -> Response:
    spa = _render_spa()
    response = make_response(spa)
    set_tracking_cookies(response=response, request=request)
    return response


def _assert_auth(auth_cookies: AuthCookies) -> None:
    if not auth_cookies.access_token or not auth_cookies.account_id or not auth_cookies.team_id:
        raise werkzeug.exceptions.Unauthorized()


def _make_response(eave_response: BaseResponseBody) -> Response:
    response = _json_response(body=eave_response.json())

    if eave_response.cookies:
        cookies = get_auth_cookies(cookies=eave_response.cookies)
        set_auth_cookies(
            response=response, access_token=cookies.access_token, account_id=cookies.account_id, team_id=cookies.team_id
        )

    return response


def _set_json_response_body(response: Response, body: JsonObject | str) -> Response:
    if not isinstance(body, str):
        body = json.dumps(body)
    response.set_data(body)
    return response


def _json_response(body: JsonObject | str) -> Response:
    response = Response(mimetype=MIME_TYPE_JSON)
    _set_json_response_body(response, body)
    return response


_status_order = [
    Status.PROCESSING,
    Status.PR_OPENED,
    Status.FAILED,
    Status.PR_CLOSED,
    Status.PR_MERGED,
]


def _document_rank(d: GithubDocument) -> str:
    """
    build a string of digits, in descending significance, to create a sorting rank. For example:

    d.status = PROCESSING
    d.status_updated = 1697060933
    rank = "01697060933"
    """
    rank = ""

    if d.status in _status_order:
        rank += str(_status_order.index(d.status))
    else:
        # put unrecognized status last
        rank += "999"

    uts = int(time.mktime(d.status_updated.timetuple()))
    rank += f"{uts}"
    return rank
