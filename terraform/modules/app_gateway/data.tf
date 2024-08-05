data "google_certificate_manager_certificate_map" "given" {
  name = var.certificate_map_name
}

data "google_compute_global_address" "given" {
  for_each = var.global_address_names
  name = each.value
}

data "google_compute_ssl_policy" "given" {
  name = var.ssl_policy_name
}