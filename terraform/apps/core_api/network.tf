resource "google_compute_global_address" "a_addrs" {
  lifecycle {
    prevent_destroy = true
  }

  count        = 1
  name         = "${local.app_name}-${count.index}"
  address_type = "EXTERNAL"
}

resource "google_dns_record_set" "default" {
  lifecycle {
    prevent_destroy = true
  }

  managed_zone = data.google_dns_managed_zone.given.name
  name         = "${local.domain_prefix}.${data.google_dns_managed_zone.given.dns_name}"
  type         = "A"
  ttl          = 300
  rrdatas = [
    for addr in google_compute_global_address.a_addrs : addr.address
  ]
}

module "api_certificate" {
  source               = "../../modules/certificate_manager"
  certificate_map_name = var.certificate_map_name
  cert_name            = local.app_name
  entry_name           = local.app_name
  hostname             = local.domain
}
