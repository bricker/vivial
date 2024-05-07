resource "kubernetes_config_map" "shared" {
  metadata {
    name = "metabase-shared"
    namespace = var.kube_namespace_name
  }

  data = {
    MB_NO_SURVEYS = "true"
    MB_SHOW_HOMEPAGE_DATA = "false"
    MB_SHOW_HOMEPAGE_XRAYS = "false"
    MB_SHOW_DATABASE_SYNCING_MODAL = "false"
    MB_LOAD_ANALYTICS_CONTENT = "false"
    MB_COLORIZE_LOGS = "false"
    MB_EMOJI_IN_LOGS = "false"
    MB_ANON_TRACKING_ENABLED = "false"
    MB_ENABLE_XRAYS = "true"
    MB_ENABLE_NESTED_QUERIES = "true"
    MB_CHECK_FOR_UPDATES = "false"
    MB_EMAIL_SMTP_HOST = "smtp-relay.gmail.com"
    MB_EMAIL_SMTP_PORT = "587"
    MB_EMAIL_SMTP_SECURITY = "tls"
    MB_EMAIL_FROM_ADDRESS = "info@eave.fyi"
    MB_EMAIL_FROM_NAME = "Eave"
    MB_ADMIN_EMAIL = "support@eave.fyi"
    MB_SEND_EMAIL_ON_FIRST_LOGIN_FROM_NEW_DEVICE = "false"
    # MB_EMAIL_REPLY_TO: "\"['info@eave.fyi']\""
    MB_ENABLE_PASSWORD_LOGIN = "true" # for Eave admins
    MB_SEND_NEW_SSO_USER_ADMIN_EMAIL = "true"
    # MB_SESSION_TIMEOUT:
    # MB_MAP_TILE_SERVER_URL:
    # MB_REPORT_TIMEZONE = America/Los_Angeles # FIXME: Can the browser's timezone be used?
    MB_ENABLE_PUBLIC_SHARING = "false"
    MB_ENABLE_EMBEDDING = "true"
    MB_EMBEDDING_APP_ORIGIN = "dashboard.${var.project.root_domain}"
    MB_SESSION_COOKIE_SAMESITE = "lax"
    MB_JWT_ENABLED = "true"
    MB_JWT_IDENTITY_PROVIDER_URI = "https://dashboard.${var.project.root_domain}"
    MB_ENABLE_QUERY_CACHING = "false"
    MB_PERSISTED_MODELS_ENABLED = "false"
    # MB_PERSISTED_MODEL_REFRESH_CRON_SCHEDULE = ""
    MB_SITE_NAME = "Eave"
    MB_APPLICATION_NAME = "Eave"
    MB_SITE_URL = "https://dashboard.${var.project.root_domain}"
    # MB_APPLICATION_FONT:
    # MB_APPLICATION_COLORS:
    # MB_APPLICATION_LOGO_URL:
    # MB_APPLICATION_FAVICON_URL:
    # MB_LANDING_PAGE:
    MB_LOADING_MESSAGE = "running-query" # This is an enum, not an arbitrary string. Setting it to an unsupported value breaks the UI!
    MB_SHOW_METABOT = "false"
    MB_SHOW_LIGHTHOUSE_ILLUSTRATION = "false"
  }
}