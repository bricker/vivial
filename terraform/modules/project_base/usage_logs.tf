# https://cloud.google.com/storage/docs/access-logs

resource "google_storage_bucket" "usage_logs" {
  lifecycle {
    prevent_destroy = true
  }

  name                        = "logs.${google_project.main.project_id}.eave.fyi"
  force_destroy               = false
  location                    = "us-central1"
  storage_class               = "ARCHIVE"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  retention_policy {
    retention_period = 31536000 # 365 days
  }

  # lifecycle_rule {
  #   action {
  #     type          = "Delete"
  #   }
  #   condition {
  #     age                        = 31536000 # 365 days
  #   }
  # }

  # logging {
  #   log_bucket = "xxx"
  # }
}