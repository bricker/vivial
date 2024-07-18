resource "google_compute_global_address" "cdn" {
  name = "cdn"
}

resource "google_dns_record_set" "cdn" {
  managed_zone = var.dns_zone.name
  name         = "cdn.${var.dns_zone.dns_name}"
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_global_address.cdn.address]
}

module "cdn_certificate" {
  source          = "../../modules/certificate_manager"
  certificate_map = var.certificate_map.name
  cert_name       = "cdn"
  entry_name      = "cdn"
  hostname        = local.domain
}