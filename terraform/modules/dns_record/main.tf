variable "address_name" {
  type = string
}

variable "domain_prefix" {
  description = "The domain prefix for each domain. Example: for 'api.eave.fyi', this value should be 'api'. Use empty string for apex domains."
  type        = string
}

variable "zone" {
  type = object({
    name     = string
    dns_name = string
  })
  description = "The DNS zone to put the DNS records in. The zone's DNS name will be used as the base domain."
}

variable "record_type" {
  type    = string
  default = "A"
}

locals {
  # eave.fyi. -> eave.fyi
  root_domain = trimsuffix(var.zone.dns_name, ".")
}

resource "google_dns_record_set" "default" {
  managed_zone = var.zone.name

  # if domain prefix given: "api.eave.fyi."
  # if domain prefix is empty string: "eave.fyi."
  name = join(".", compact([var.domain_prefix, var.zone.dns_name]))

  type = "A"
  ttl  = 300

  rrdatas = [var.address_name]
}

output "records" {
  value = join(".", compact([var.domain_prefix, local.root_domain]))
}