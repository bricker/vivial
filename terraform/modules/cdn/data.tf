data "google_project" "default" {}

data "google_certificate_manager_certificate_map" "given" {
  depends_on = [ var.certificate_map_name ]
  name = var.certificate_map_name
}

data "google_dns_managed_zone" "given" {
  depends_on = [ var.dns_zone_name ]
  name = var.dns_zone_name
}

data "google_compute_ssl_policy" "given" {
  depends_on = [ var.ssl_policy_name ]
  name = var.ssl_policy_name
}

data "google_storage_bucket" "usage_logs" {
  depends_on = [ var.usage_logs_bucket_name ]
  name = var.usage_logs_bucket_name
}