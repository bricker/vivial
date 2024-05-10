variable "certificate_map" {
  type=string
}

variable "cert_name" {
  type=string
}

variable "entry_name" {
  type=string
}

variable "hostname" {
  type=string
}

variable "domains" {
  type=list(string)
  description = "If not given, the hostname will be used"
  nullable = true
  default = null
}

resource "google_certificate_manager_certificate" "default" {
  name        = var.cert_name
  managed {
    domains = var.domains != null ? var.domains : [var.hostname]
  }
}

resource "google_certificate_manager_certificate_map_entry" "default" {
  map         = var.certificate_map
  name        = var.entry_name
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


