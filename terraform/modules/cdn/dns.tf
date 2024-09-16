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

  managed_zone = data.google_dns_managed_zone.given.name
  name         = "${var.name}.${data.google_dns_managed_zone.given.dns_name}"
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_global_address.default.address]
}

module "cdn_certificate" {
  source               = "../../modules/certificate_manager"
  certificate_map_name = var.certificate_map_name
  cert_name            = var.name
  entry_name           = var.name
  hostname             = local.domain
}