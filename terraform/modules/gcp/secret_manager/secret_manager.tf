// https://registry.terraform.io/modules/GoogleCloudPlatform/secret-manager/google/latest

locals {
  secrets = toset([
    "EAVE_ATLASSIAN_APP_CLIENT_ID",
    "EAVE_ATLASSIAN_APP_CLIENT_SECRET",
    "EAVE_API_BASE_PUBLIC",
    "EAVE_APPS_BASE_PUBLIC",
    "EAVE_WWW_BASE_PUBLIC",
    "EAVE_DB_HOST",
    "EAVE_DB_NAME",
    "EAVE_DB_PASS",
    "EAVE_DB_USER",
    "EAVE_GITHUB_APP_CLIENT_ID",
    "EAVE_GITHUB_APP_CLIENT_SECRET",
    "EAVE_GITHUB_APP_CRON_SECRET",
    "EAVE_GITHUB_APP_ID",
    "EAVE_GITHUB_APP_PRIVATE_KEY",
    "EAVE_GITHUB_APP_WEBHOOK_SECRET",
    "EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON",
    "EAVE_SLACK_APP_CLIENT_ID",
    "EAVE_SLACK_APP_CLIENT_SECRET",
    "EAVE_SLACK_APP_ID",
    "EAVE_SLACK_APP_SIGNING_SECRET",
    "EAVE_SLACK_APP_SOCKETMODE_TOKEN",
    "OPENAI_API_KEY",
    "OPENAI_API_ORG",
    "SLACK_SYSTEM_BOT_TOKEN",
  ])
}

resource "google_secret_manager_secret" "all" {
  for_each = local.secrets

  secret_id   = each.key
  expire_time = null
  labels      = {}
  ttl         = null

  replication {
    automatic = true
  }
}
