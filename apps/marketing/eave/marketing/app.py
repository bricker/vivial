from typing import Any

import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api
import eave.stdlib.core_api.client as eave_core
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.logging
import eave.stdlib.time
from flask import Flask, render_template, request

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


@app.route("/dashboard/account", methods=["GET"])
async def get_current_account() -> str:
    return "OK"


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
