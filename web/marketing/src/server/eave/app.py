import json
from http import HTTPStatus
from typing import Any

import eave.settings
from flask import Flask, redirect, render_template, session
from werkzeug import Response

app = Flask(__name__)
app.secret_key = eave.settings.APP_SETTINGS.eave_web_session_encryption_key


@app.get("/status")
def status() -> dict[str, str]:
    return {
        "service": "www",
        "status": "OK",
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
