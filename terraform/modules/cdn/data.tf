data "google_storage_bucket" "usage_logs" {
  name = var.usage_logs_bucket_name
}