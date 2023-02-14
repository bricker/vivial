import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, redirect, render_template
from werkzeug import Response

load_dotenv()

app = Flask(__name__)


class AppConfiguration:
    @property
    def app_env(self) -> str:
        if app.debug:
            return "development"
        else:
            return "production"

    @property
    def analytics_enabled(self) -> bool:
        return os.getenv("EAVE_ANALYTICS_ENABLED") is not None

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONIORING_ENABLED") is not None

    @property
    def app_version(self) -> str:
        return os.getenv("GAE_VERSION", "development")

    @property
    def cookie_domain(self) -> str:
        return os.getenv("EAVE_COOKIE_DOMAIN", ".eave.fyi")

    @property
    def api_base(self) -> str:
        return os.getenv("EAVE_API_BASE", "https://api.eave.fyi")

    @property
    def asset_base(self) -> str:
        return os.getenv("EAVE_ASSET_BASE", "/static")


APP_CONFIG = AppConfiguration()


@app.route("/status")
@app.route("/_ah/start")
@app.route("/_ah/stop")
@app.route("/_ah/warmup")
def status() -> dict[str, str]:
    return {"status": "1"}


@app.route("/")
def spa_home() -> str:
    return _render_spa()


@app.route("/early")
def spa_early() -> str:
    return _render_spa()


@app.route("/<path:path>")
def catch_all(**kwargs: Any) -> Response:
    return redirect(location="/", code=302)


def _render_spa(**kwargs: Any) -> str:
    return render_template(
        "index.html.jinja",
        app_config=APP_CONFIG,
        **kwargs,
    )
