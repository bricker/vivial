export const EAVE_TEAM_ID_HEADER = "eave-team-id";
export const EAVE_ACCOUNT_ID_HEADER = "eave-account-id";
export const EAVE_SIGNATURE_HEADER = "eave-signature";
export const EAVE_SIG_TS_HEADER = "eave-sig-ts";
export const EAVE_ORIGIN_HEADER = "eave-origin";
export const EAVE_REQUEST_ID_HEADER = "eave-request-id";

/*
This header can be used to bypass certain checks in development, like payload signing.
It works because Google removes all "X-Google-*" headers on incoming requests, so if this header
is present, we can be reasonably sure that this is a development machine.
*/
export const EAVE_DEV_BYPASS_HEADER = "x-google-eavedev";

// For express Response.locals[EAVE_CTX_KEY]
export const EAVE_CTX_KEY = "eave-ctx";

// Request headers added by Google
export const GCP_CLOUD_TRACE_CONTEXT = "x-cloud-trace-context";
export const GCP_GAE_REQUEST_LOG_ID = "x-appengine-request-log-id";
export const GCP_GAE_TASK_EXECUTION_COUNT = "x-appengine-taskexecutioncount";

export const MIME_TYPE_JSON = "application/json";
