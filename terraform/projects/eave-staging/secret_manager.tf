# These are individual variables instead of a single map+iteration so that all of the expected secrets are required to be set.
# If any of these aren't set, terraform apply won't run.
# Additionally, a map with `sensitive=true` can't be used for iteration.

# variable "METABASE_JWT_KEY" {
#   type      = string
#   sensitive = true
# }

variable "EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64" {
  type      = string
  sensitive = true
}

variable "SLACK_SYSTEM_BOT_TOKEN" {
  type      = string
  sensitive = true
}

locals {
  secrets = {
    "EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64" = var.EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64
    "SLACK_SYSTEM_BOT_TOKEN"                        = var.SLACK_SYSTEM_BOT_TOKEN
  }
}

resource "google_secret_manager_secret" "secrets" {
  for_each = local.secrets

  secret_id = each.key

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "secret_versions" {
  for_each = google_secret_manager_secret.secrets

  secret = each.value.id

  secret_data = local.secrets[each.key]
}

# resource "google_secret_manager_secret_iam_binding" "binding" {
#   project = google_secret_manager_secret.secret-basic.project
#   secret_id = google_secret_manager_secret.secret-basic.secret_id
#   role = "roles/secretmanager.secretAccessor"
#   members = [
#     "user:jane@example.com",
#   ]
# }