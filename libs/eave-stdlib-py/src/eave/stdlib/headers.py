# Eave-specific request headers
EAVE_TEAM_ID_HEADER = "eave-team-id"
EAVE_ACCOUNT_ID_HEADER = "eave-account-id"
EAVE_SIGNATURE_HEADER = "eave-signature"
EAVE_SIG_TS_HEADER = "eave-sig-ts"
EAVE_ORIGIN_HEADER = "eave-origin"
EAVE_REQUEST_ID_HEADER = "eave-request-id"
EAVE_CRON_DISPATCH_KEY_HEADER = "eave-cron-dispatch-key"

EAVE_DEV_BYPASS_HEADER = "X-Google-EAVEDEV"
"""
This header can be used to bypass certain checks in development, like payload signing.
It works because Google removes all "X-Google-*" headers on incoming requests, so if this header
is present, we can be reasonably sure that this is a development machine.
"""

# Well-known request headers
COOKIE_HEADER = "cookie"
SET_COOKIE_HEADER = "set-cookie"
AUTHORIZATION_HEADER = "authorization"
HOST = "host"
CONTENT_TYPE = "content-type"
CONTENT_LENGTH = "content-length"
USER_AGENT = "user-agent"

# Request headers added by Google
GCP_CLOUD_TRACE_CONTEXT = "X-Cloud-Trace-Context"
GCP_GAE_REQUEST_LOG_ID = "X-Appengine-Request-Log-Id"
GCP_GAE_TASK_EXECUTION_COUNT = "X-AppEngine-TaskExecutionCount"

MIME_TYPE_JSON = "application/json"
MIME_TYPE_TEXT = "text/plain"
