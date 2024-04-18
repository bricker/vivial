variable "domain_prefix" {
  type        = string
  description = "The domain prefix. Example: for 'api.eave.fyi', this value should be 'api'. Use empty string for apex domains."
  validation {
    condition     = can(regex("[^\\.]?$", var.domain_prefix))
    error_message = "domain_prefix should not end with a dot"
  }
}

variable "zone" {
  type = object({
    name     = string
    dns_name = string
  })
  description = "The DNS zone to put the DNS records in. The zone's DNS name will be used as the base domain."
}

locals {
  # eave.fyi. -> eave.fyi
  root_domain = trimsuffix(var.zone.dns_name, ".")
}

resource "google_compute_global_address" "default" {
  # api.eave.fyi -> api-dot-eave-dot-fyi
  name         = join("", [replace("${var.domain_prefix}.${local.root_domain}", ".", "-dot-"), "-addr"])
  address_type = "EXTERNAL"
}

resource "google_dns_record_set" "a" {
  managed_zone = var.zone.name

  # if domain prefix given: "api.eave.fyi."
  # if domain prefix is empty string: "eave.fyi."
  name = join(".", compact([var.domain_prefix, var.zone.dns_name]))

  type = "A"
  ttl  = 300

  rrdatas = [google_compute_global_address.default.address]
}
