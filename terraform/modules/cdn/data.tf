data "google_storage_bucket" "usage_logs" {
  # depends_on = [var.usage_logs_bucket_name] # Necessary for the TF dependency graph
  name = var.usage_logs_bucket_name
}