# FIXME: This was a temporary hack to get the certificate provisioned ASAP
resource "google_certificate_manager_dns_authorization" "dashboard" {
  name   = "dashboard-dns-auth"
  domain = "www.vivialapp.com"
}

resource "google_certificate_manager_certificate" "dashboard" {
  lifecycle {
    prevent_destroy = true
  }

  name = "dashboard"
  managed {
    domains            = ["www.vivialapp.com"]
    dns_authorizations = [google_certificate_manager_dns_authorization.dashboard.id]
  }
}

resource "google_certificate_manager_certificate_map_entry" "dashboard" {
  lifecycle {
    prevent_destroy = true
  }

  map          = module.project_base.google_certificate_manager_certificate_map.name
  name         = "dashboard"
  certificates = [google_certificate_manager_certificate.dashboard.id]
  hostname     = "www.vivialapp.com"
}
