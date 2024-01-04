from multidict import istr


# Eave-specific request headers
EAVE_TEAM_ID_HEADER = istr("eave-team-id")
EAVE_ACCOUNT_ID_HEADER = istr("eave-account-id")
EAVE_SIGNATURE_HEADER = istr("eave-signature")
EAVE_SIG_TS_HEADER = istr("eave-sig-ts")
EAVE_ORIGIN_HEADER = istr("eave-origin")
EAVE_REQUEST_ID_HEADER = istr("eave-request-id")
EAVE_CRON_DISPATCH_KEY_HEADER = istr("eave-cron-dispatch-key")
EAVE_CLIENT_ID = istr("eave-client-id")
EAVE_CLIENT_SECRET = istr("eave-client-secret")

EAVE_DEV_BYPASS_HEADER = istr("X-Google-EAVEDEV")
"""
This header can be used to bypass certain checks in development, like payload signing.
It works because Google removes all "X-Google-*" headers on incoming requests, so if this header
is present, we can be reasonably sure that this is a development machine.
"""

# Request headers added by Google
GCP_CLOUD_TRACE_CONTEXT = istr("X-Cloud-Trace-Context")
GCP_GAE_REQUEST_LOG_ID = istr("X-Appengine-Request-Log-Id")
GCP_GAE_TASK_EXECUTION_COUNT = istr("X-AppEngine-TaskExecutionCount")

MIME_TYPE_JSON = "application/json"
MIME_TYPE_TEXT = "text/plain"
ENCODING_GZIP = "gzip"
ENCODING_DEFLATE = "deflate"