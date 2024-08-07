data "google_project" "default" {}

data "google_certificate_manager_certificate_map" "given" {
  name = var.certificate_map_name
}

data "google_dns_managed_zone" "given" {
  name = var.dns_zone_name
}

data "google_compute_ssl_policy" "given" {
  name = var.ssl_policy_name
}