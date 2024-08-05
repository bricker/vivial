data "google_dns_managed_zone" "given" {
  name = var.dns_zone_name
}

data "google_compute_global_address" "given" {
  name = var.global_address_name
}