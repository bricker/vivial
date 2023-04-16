import eave.stdlib.api_util
import eave.stdlib.logging
from fastapi import FastAPI

from .public.requests import access_requests, documents, subscriptions
from .public.requests import util as eave_request_util
from .public.requests.oauth_handlers import atlassian_oauth, google_oauth, slack_oauth

eave.stdlib.logging.setup_logging()

app = FastAPI()

eave.stdlib.api_util.add_standard_endpoints(app=app)
eave_request_util.add_standard_exception_handlers(app=app)

app.post("/access_request")(access_requests.create_access_request)
app.post("/documents/upsert")(documents.upsert_document)
app.post("/subscriptions/create")(subscriptions.create_subscription)
app.post("/subscriptions/query")(subscriptions.get_subscription)
app.post("/subscriptions/delete")(subscriptions.delete_subscription)
app.get("/oauth/google/authorize")(google_oauth.google_oauth_authorize)
app.get("/oauth/google/callback")(google_oauth.google_oauth_callback)
app.get("/oauth/slack/authorize")(slack_oauth.slack_oauth_authorize)
app.get("/oauth/slack/callback")(slack_oauth.slack_oauth_callback)
app.get("/oauth/atlassian/authorize")(atlassian_oauth.atlassian_oauth_authorize)
app.get("/oauth/atlassian/callback")(atlassian_oauth.atlassian_oauth_callback)
