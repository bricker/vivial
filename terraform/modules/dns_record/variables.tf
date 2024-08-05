variable "global_address_name" {
  type = string
}

variable "dns_zone_name" {
  type = string
  description = "The DNS zone to put the DNS records in. The zone's DNS name will be used as the base domain."
}

variable "domain_prefix" {
  description = "The domain prefix for each domain. Example: for 'api.eave.fyi', this value should be 'api'. Use empty string for apex domains."
  type        = string
}

variable "record_type" {
  type    = string
  default = "A"
}