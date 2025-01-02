resource "google_certificate_manager_dns_authorization" "default" {
  lifecycle {
    prevent_destroy = true
  }

  count = var.dns_authorization ? 1 : 0
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
    dns_authorizations = var.dns_authorization ? [google_certificate_manager_dns_authorization.default[0].id] : null
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

# DNS Authorization example:

# resource "google_certificate_manager_dns_authorization" "instance" {
#   name        = "dns-auth"
#   description = "The default dnss"
#   domain      = "subdomain.hashicorptest.com"
# }

# resource "google_certificate_manager_certificate" "certificate" {
#   name        = "cert-map-entry"
#   description = "The default cert"
#   scope       = "DEFAULT"
#   managed {
#     domains = [
#       google_certificate_manager_dns_authorization.instance.domain,
#     ]
#     dns_authorizations = [
#       google_certificate_manager_dns_authorization.instance.id,
#     ]
#   }
# }
