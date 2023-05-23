# Eave-specific request headers
EAVE_TEAM_ID_HEADER = "eave-team-id"
EAVE_ACCOUNT_ID_HEADER = "eave-account-id"
EAVE_SIGNATURE_HEADER = "eave-signature"
EAVE_ORIGIN_HEADER = "eave-origin"
EAVE_REQUEST_ID_HEADER = "eave-request-id"

EAVE_DEV_BYPASS_HEADER = "X-Google-EAVEDEV"
"""
This header can be used to bypass certain checks in development, like payload signing.
It works because Google removes all "X-Google-*" headers on incoming requests, so if this header
is present, we can be reasonably sure that this is a development machine.
"""

# Well-known request headers
AUTHORIZATION_HEADER = "authorization"
CONTENT_TYPE = "content-type"
COOKIE_HEADER = "cookie"

# Request headers added by Google
GCP_CLOUD_TRACE_CONTEXT = "X-Cloud-Trace-Context"
GCP_GAE_REQUEST_LOG_ID = "X-Appengine-Request-Log-Id"
GCP_GAE_TASK_EXECUTION_COUNT = "X-AppEngine-TaskExecutionCount"
