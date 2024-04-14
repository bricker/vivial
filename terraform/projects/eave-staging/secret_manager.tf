variable "METABASE_JWT_KEY" {
  type=string
  sensitive = true
}

locals {
  secrets = {
    "METABASE_JWT_KEY" = var.METABASE_JWT_KEY
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