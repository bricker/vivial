from http import HTTPStatus
from typing import Any

import eave.settings
from flask import Flask, redirect, render_template, session
from werkzeug import Response

app = Flask(__name__)
app.secret_key = eave.settings.APP_SETTINGS.eave_web_session_encryption_key


@app.get("/status")
@app.get("/_ah/start")
@app.get("/_ah/stop")
@app.get("/_ah/warmup")
def status() -> dict[str, str]:
    return {
        "status": "1",
        "service": "www",
    }


@app.get("/")
def spa_home() -> str:
    return _render_spa()


@app.get("/early")
def spa_early() -> str:
    return _render_spa()


@app.route("/<path:path>")
def catch_all(**kwargs: Any) -> Response:
    return redirect(location="/", code=HTTPStatus.FOUND)


def _render_spa(**kwargs: Any) -> str:
    return render_template(
        "index.html.jinja",
        app_config=eave.settings.APP_SETTINGS,
        **kwargs,
    )
