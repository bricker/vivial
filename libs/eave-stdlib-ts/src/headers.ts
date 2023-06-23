// Express lowercases all header names, so these should all be lowercased.

export default {
  EAVE_TEAM_ID_HEADER: 'eave-team-id',
  EAVE_ACCOUNT_ID_HEADER: 'eave-account-id',
  EAVE_SIGNATURE_HEADER: 'eave-signature',
  EAVE_ORIGIN_HEADER: 'eave-origin',
  EAVE_REQUEST_ID_HEADER: 'eave-request-id',

  /* well-known headers */
  COOKIE_HEADER: 'cookie',
  AUTHORIZATION_HEADER: 'authorization',

  /*
  This header can be used to bypass certain checks in development, like payload signing.
  It works because Google removes all "X-Google-*" headers on incoming requests, so if this header
  is present, we can be reasonably sure that this is a development machine.
  */
  EAVE_DEV_BYPASS_HEADER: 'x-google-eavedev',

  // For express Response.locals[EAVE_CTX_KEY]
  EAVE_CTX_KEY: 'eave-ctx',
};
