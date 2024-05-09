# resource "google_certificate_manager_certificate" "certificate" {
#   name        = "cert-map-entry"
#   description = "The default cert"
#   scope       = "DEFAULT"
#   managed {
#     domains = [
#       google_certificate_manager_dns_authorization.instance.domain,
#       google_certificate_manager_dns_authorization.instance2.domain,
#       ]
#     dns_authorizations = [
#       google_certificate_manager_dns_authorization.instance.id,
#       google_certificate_manager_dns_authorization.instance2.id,
#       ]
#   }
# }


variable "cert_name" {
  type=string
}

variable "domains" {
  type=list(string)
}

resource "google_certificate_manager_certificate" "default" {
  name        = var.cert_name
  managed {
    domains = var.domains
  }
}

resource "google_certificate_manager_certificate_map_entry" "default" {
  name        = "${local.name}-first-entry"
  map         = google_certificate_manager_certificate_map.default.name
  certificates = [google_certificate_manager_certificate.default.id]
  hostname     = local.project.root_domain
}

# resource "google_certificate_manager_certificate" "default" {
#   name        = var.cert_name
#   managed {
#     domains = var.domains
#   }
# }

resource "google_certificate_manager_certificate_map" "default" {
  name        = "root-certificate-map"
  description = "${local.domain} certificate map"
}

resource "google_certificate_manager_certificate_map_entry" "default" {
  name        = "${local.name}-first-entry"
  map         = google_certificate_manager_certificate_map.default.name
  certificates = [google_certificate_manager_certificate.default.id]
  hostname     = local.domain
}

# resource "google_certificate_manager_certificate_map" "default" {
#   name        = "wildcard-certificate-map"
# }

# resource "google_certificate_manager_certificate_map_entry" "default" {
#   name        = "wildcard-certificate-map-entry"
#   map = google_certificate_manager_certificate_map.default.name
#   certificates = [google_certificate_manager_certificate.certificate.id]
#   matcher = "PRIMARY"
# }



# resource "google_certificate_manager_dns_authorization" "instance" {
#   name        = "dns-auth"
#   description = "The default dnss"
#   domain      = "subdomain.hashicorptest.com"
# }

# resource "google_certificate_manager_dns_authorization" "instance2" {
#   name        = "dns-auth2"
#   description = "The default dnss"
#   domain      = "subdomain2.hashicorptest.com"
# }