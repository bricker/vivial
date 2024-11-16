variable "name" {
  type = string
}

variable "resource_domain" {
  type = string
}

variable "google_dns_managed_zone" {
  type = object({
    name = string
    dns_name = string
  })
}

variable "google_certificate_manager_certificate_map" {
  type = object({
    id = string
    name = string
  })
}

variable "google_compute_ssl_policy" {
  type = object({
    name = string
  })
}

variable "usage_logs_bucket_name" {
  type = string
}