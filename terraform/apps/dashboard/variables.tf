variable "public_domain_prefix" {
  type    = string
  default = "www"
}

variable "environment" {
  description = "Allowed values: DEV, STG, PROD"
  type        = string
  default     = "DEV"

  validation {
    condition     = contains(["DEV", "STG", "PROD"], var.environment)
    error_message = "Allowed values: DEV, STG, PROD"
  }
}

variable "google_dns_managed_zone" {
  type = object({
    name     = string
    dns_name = string
  })
}

variable "google_compute_ssl_policy" {
  type = object({
    name = string
  })
}

variable "google_certificate_manager_certificate_map" {
  type = object({
    id   = string
    name = string
  })
}

variable "docker_repository_ref" {
  type = object({
    location      = string
    repository_id = string
  })
}

variable "kube_namespace_name" {
  type = string
}

variable "shared_config_map_name" {
  type = string
}

variable "cdn_base_url" {
  type = string
}

variable "release_version" {
  type = string
}

variable "LOG_LEVEL" {
  type    = string
  default = "debug"
}

variable "iap_oauth_client_id" {
  type     = string
  nullable = true
  default  = null
}

variable "iap_oauth_client_kube_secret_name" {
  type     = string
  nullable = true
  default  = null
}

variable "iap_enabled" {
  type    = bool
  default = false
}
