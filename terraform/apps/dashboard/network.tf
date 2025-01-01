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

  managed_zone = var.google_dns_managed_zone.name
  name         = "${var.public_domain_prefix}.${var.google_dns_managed_zone.dns_name}"
  type         = "A"
  ttl          = 300
  rrdatas = [
    for addr in google_compute_global_address.a_addrs : addr.address
  ]
}

# module "certificate" {
#   source                                     = "../../modules/certificate_manager"
#   google_certificate_manager_certificate_map = var.google_certificate_manager_certificate_map
#   cert_name                                  = local.app_name
#   entry_name                                 = local.app_name
#   hostname                                   = local.domain
# }
