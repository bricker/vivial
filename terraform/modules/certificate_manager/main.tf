resource "google_certificate_manager_dns_authorization" "default" {
  lifecycle {
    prevent_destroy = true
  }

  count = var.use_dns_authorization ? 1 : 0

  name   = "${var.cert_name}-dns-auth"
  domain = var.hostname
}

resource "google_certificate_manager_certificate" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name = var.cert_name
  managed {
    domains = [var.hostname]
    dns_authorizations = var.use_dns_authorization ? [
      for dns_auth in google_certificate_manager_dns_authorization.default : dns_auth.id
    ] : null
  }
}

resource "google_certificate_manager_certificate_map_entry" "default" {
  lifecycle {
    prevent_destroy = true
  }

  map          = var.google_certificate_manager_certificate_map.name
  name         = var.entry_name
  certificates = [google_certificate_manager_certificate.default.id]
  hostname     = var.hostname
}
