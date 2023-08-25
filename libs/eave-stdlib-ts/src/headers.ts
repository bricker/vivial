import http2 from 'node:http2';

export default {
  EAVE_TEAM_ID_HEADER: 'eave-team-id',
  EAVE_ACCOUNT_ID_HEADER: 'eave-account-id',
  EAVE_SIGNATURE_HEADER: 'eave-signature',
  EAVE_ORIGIN_HEADER: 'eave-origin',
  EAVE_REQUEST_ID_HEADER: 'eave-request-id',

  /*
  This header can be used to bypass certain checks in development, like payload signing.
  It works because Google removes all "X-Google-*" headers on incoming requests, so if this header
  is present, we can be reasonably sure that this is a development machine.
  */
  EAVE_DEV_BYPASS_HEADER: 'x-google-eavedev',

  // For express Response.locals[EAVE_CTX_KEY]
  EAVE_CTX_KEY: 'eave-ctx',

  // Request headers added by Google
  GCP_CLOUD_TRACE_CONTEXT: 'x-cloud-trace-context',
  GCP_GAE_REQUEST_LOG_ID: 'x-appengine-request-log-id',
  GCP_GAE_TASK_EXECUTION_COUNT: 'x-appengine-taskexecutioncount',

  MIME_TYPE_JSON: 'application/json',
};
