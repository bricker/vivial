resource "google_secret_manager_secret" "default" {
  secret_id = var.secret_id

  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "default" {
  secret      = google_secret_manager_secret.default.id
  secret_data = var.secret_data
}

resource "google_secret_manager_secret_iam_binding" "default" {
  secret_id = google_secret_manager_secret.default.secret_id
  role = "roles/secretmanager.secretAccessor"
  members = var.accessors
}
