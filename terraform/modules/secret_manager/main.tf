resource "google_secret_manager_secret" "default" {
  # Create the secret with no versions.
  secret_id = var.secret_id

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "default" {
  # Create a version. If the data changes, Terraform will create a new version.
  secret      = google_secret_manager_secret.default.id
  secret_data = var.secret_data
}

resource "google_secret_manager_secret_iam_binding" "default" {
  # Grant "accessors" access to this secret
  secret_id = google_secret_manager_secret.default.secret_id
  role = var.secret_accessor_role_id
  members = var.accessors
}
