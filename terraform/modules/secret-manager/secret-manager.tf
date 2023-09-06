// https://registry.terraform.io/modules/GoogleCloudPlatform/secret-manager/google/latest

resource "google_secret_manager_secret" "all" {
  for_each = toset([
    "EAVE_DB_HOST",
    "EAVE_DB_USER",
    "EAVE_DB_PASS",
    "EAVE_DB_NAME",
    "EAVE_ATLASSIAN_APP_CLIENT_ID",
    "EAVE_ATLASSIAN_APP_CLIENT_SECRET",
    "EAVE_GITHUB_APP_ID",
    "EAVE_GITHUB_APP_CLIENT_ID",
    "EAVE_GITHUB_APP_CLIENT_SECRET",
    "EAVE_GITHUB_APP_PRIVATE_KEY",
    "EAVE_GITHUB_APP_WEBHOOK_SECRET",
    "EAVE_SLACK_APP_CLIENT_ID",
    "EAVE_SLACK_APP_CLIENT_SECRET",
    "EAVE_SLACK_APP_ID",
    "EAVE_SLACK_APP_SIGNING_SECRET",
    "EAVE_SLACK_APP_SOCKETMODE_TOKEN",
    "OPENAI_API_KEY",
    "OPENAI_API_ORG",
  ])

  secret_id   = each.key
  expire_time = null
  labels      = {}
  ttl         = null
  replication {
    automatic = true
  }
}
