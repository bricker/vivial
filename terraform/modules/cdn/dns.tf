resource "google_compute_global_address" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name = var.name
}

resource "google_dns_record_set" "default" {
  lifecycle {
    prevent_destroy = true
  }

  managed_zone = var.google_dns_managed_zone.name
  name         = "${var.name}.${var.google_dns_managed_zone.dns_name}"
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_global_address.default.address]
}

module "cdn_certificate" {
  source               = "../../modules/certificate_manager"
  google_certificate_manager_certificate_map = var.google_certificate_manager_certificate_map
  cert_name            = var.name
  entry_name           = var.name
  hostname             = local.domain
}